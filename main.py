import asyncio
import json
import time
from itertools import chain

import aiofiles
import aiohttp

from config import URL, HEADERS
from parser import get_menu_categories, get_level_first_subcategories, get_level_second_subcategories, \
	check_product_count, extract_page_count, extract_category_title, extract_product_urls, extract_product_info
from сonnect import get_response_text


async def get_total_urls_second_subcategories(url: str):
	total_urls_second_subcategories = []

	async with aiohttp.ClientSession(headers=HEADERS) as session:
		semaphore = asyncio.Semaphore(10)
		data = await get_response_text(session, url)
		menu_categories = await get_menu_categories(data)
		data_categories = await asyncio.gather(*(get_response_text(session, URL + url_cat)
												 for url_cat in menu_categories[4:]))

		for data_cat in data_categories[:2]:
			urls_level_first_subcategories = await get_level_first_subcategories(data_cat)

			data_categories_tree = await asyncio.gather(*(get_response_text(session, URL + url_cat)
														  for url_cat in urls_level_first_subcategories))

			urls_and_title_level_second_subcategories = await asyncio.gather(
				*(get_level_second_subcategories(data_sub_cat) for data_sub_cat in data_categories_tree[:1]))
			total_urls_second_subcategories += list(chain.from_iterable(urls_and_title_level_second_subcategories))

	return total_urls_second_subcategories


async def main(url):
	data = {}
	async with aiohttp.ClientSession(headers=HEADERS) as session:
		semaphore = asyncio.Semaphore(10)
		total_urls_second_subcategories = await get_total_urls_second_subcategories(url)

		for url_cat in total_urls_second_subcategories:
			data_category = await get_response_text(session, URL + url_cat)

			if await check_product_count(data_category):
				tip_cat = await extract_category_title(data_category)
				data[tip_cat] = []
				pages = await extract_page_count(data_category)
				pages_urls = [url_cat] + [f"{url_cat}?pages{i}" for i in range(2, pages + 1)]
				total_data_sub_category = await asyncio.gather(
					*(get_response_text(session, URL + url) for url in pages_urls))
				for page in total_data_sub_category:
					urls_product_page = await extract_product_urls(page)

					total_data_products_html = await asyncio.gather(
						*(get_response_text(session, URL + url_product) for url_product in urls_product_page))

					total_data_products = await asyncio.gather(
						*(extract_product_info(data_product_html) for data_product_html in total_data_products_html))
					data[tip_cat].append(total_data_products)
			async with aiofiles.open("data.json", "a+", encoding="utf-8") as f:
				await f.write(json.dumps(data, indent=4, ensure_ascii=False))
			break


if __name__ == '__main__':
	start = time.time()
	asyncio.run(main(URL))
	end = time.time()
	print(f'Время: {round((end - start) / 60)} мин.')
