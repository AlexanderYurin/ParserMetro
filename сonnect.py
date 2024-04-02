import aiohttp

from config import HEADERS


async def get_response_text(session, url: str) -> str:
	async with session.get(url, ssl=False) as resp:
		if resp.status == 200:
			resp_text = await resp.text()
			return resp_text
