from typing import List, Dict

from bs4 import BeautifulSoup as bs

from config import QUANTITY_PRODUCT


async def get_menu_categories(data: str) -> List[str]:
    """
    Получает ссылки на категории из меню.
    :param data: HTML-код страницы.
    :return Список ссылок на категории.
    """
    soup = bs(data, "lxml")
    categories_html = soup.find_all(name="a", attrs={"class": "menu-item"})
    return [category_html.get("href") for category_html in categories_html]


async def get_level_first_subcategories(data: str) -> List[str]:
    """
    Получает ссылки на подкатегории первого уровня.
    :param data: HTML-код страницы.
    :return Список ссылок на подкатегории первого уровня.
    """
    soup = bs(data, "lxml")
    sub_categories = soup.find_all(attrs={"class": "catalog-filters-categories__item level-first is-bold"})
    return [category_html.get("href") for category_html in sub_categories]


async def get_level_second_subcategories(data: str) -> List[str]:
    """
    Получает ссылки и названия на подкатегории второго уровня.
    :param data: HTML-код страницы.
    :return Список кортежей (ссылка, название) на подкатегории второго уровня.
    """
    soup = bs(data, "lxml")
    sub_categories = soup.find_all(attrs={"class": "catalog-filters-categories__item level-second"}) or \
                     soup.find_all(attrs={
                         "class": "nuxt-link-exact-active nuxt-link-active catalog-filters-categories__item level-first"})
    return [category_html.get("href") for category_html in sub_categories]


async def extract_product_urls(html_data: str) -> List[str]:
    """
    Извлекает URL-адреса продуктов из HTML-данных.
    :param html_data: HTML-данные страницы категории.
    :return: Список URL-адресов продуктов.
    """
    soup = bs(html_data, "lxml")
    product_data = soup.find_all(name="a", attrs={"data-qa": "product-card-photo-link"})
    return [category_html.get("href") for category_html in product_data]


async def check_product_count(html_data: str) -> bool:
    """
    Проверяет количество продуктов на странице категории.
    :param html_data: HTML-данные страницы категории.
    :return: True, если количество продуктов достаточно, иначе False.
    """
    soup = bs(html_data, "lxml")
    product_count_data = soup.find(attrs="heading-products-count subcategory-or-type__heading-count")
    num = product_count_data.text.split()[0]
    if num.isdigit():
        return int(num) >= QUANTITY_PRODUCT
    return False


async def extract_product_info(html_data: str) -> Dict:
    """
    Извлекает информацию о продукте из HTML-данных страницы продукта.
    :param html_data: HTML-данные страницы продукта.
    :return: Словарь с информацией о продукте.
    """
    soup = bs(html_data, "lxml")
    availability_check = soup.find(
        name="p",
        attrs={"class": "product-title product-page-content__title-out-of-stock style--product-page"}
    )
    if not availability_check:
        article = soup.find(attrs="product-page-content__article").get_text(strip=True).split()[1]
        title = soup.find(
            name="h1",
            attrs={"class": "product-page-content__product-name catalog-heading heading__h2"}
        ).get_text(strip=True)
        brand = soup.find(name="meta", attrs={"itemprop": "brand"}).get("content", "Нет бренда")

        try:
            promo_price = "".join(soup.find(
                name="div",
                attrs={"class": "product-unit-prices__actual-wrapper"}
            ).find(name="span", attrs={"class": "product-price__sum-rubles"}).text.split())
        except AttributeError:
            promo_price = None

        try:
            old_price = soup.find(
                name="div",
                attrs={"class": "product-unit-prices__old-wrapper"}
            ).find(name="span", attrs={"class": "product-price__sum-rubles"})
            if not old_price:
                old_price = promo_price
            else:
                old_price = "".join(old_price.text.split())
        except AttributeError:
            old_price = None

        return {"article": article, "title": title, "promo_price": promo_price, "brand": brand, "old_price": old_price}


async def extract_page_count(html_data: str) -> int:
    """
    Извлекает количество страниц в пагинации.
    :param html_data: HTML-данные страницы категории.
    :return: Количество страниц.
    """
    soup = bs(html_data, "lxml")
    pages = soup.find_all(name="a", attrs={"class": "v-pagination__item catalog-paginate__item"})
    return max(map(int, [page.get_text(strip=True) for page in pages]), default=0)


async def extract_category_title(html_data: str) -> str:
    """
    Извлекает заголовок категории.
    :param html_data: HTML-данные страницы категории.
    :return: Заголовок категории.
    """
    soup = bs(html_data, "lxml")
    return soup.find(
        name="h1",
        attrs={"class": "subcategory-or-type__heading-title catalog-heading heading__h1"}
    ).get_text(strip=True)






