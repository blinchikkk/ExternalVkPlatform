import aiohttp, ujson, asyncio, logging

from typing import Optional


URL = "https://api.vk.com/method/"

# If the request is unsuccessful, the function tries to repeat
# it until the number of requests reaches Maximum Number Requests
MNR = 60


async def get(url: str = URL, method: str = "", params: dict = {}, iteration: int = 0, test: bool = 0) -> Optional[dict]:
	"""
	Asynchronous function for GET requests that accepts 
	url <url> and method <method> and parameters <params>
	"""

	session = aiohttp.ClientSession(
			json_serialize=ujson.dumps,
			trust_env = True, 
			connector=aiohttp.TCPConnector(verify_ssl=False)
	)

	try:
		async with session.get(f'{url}{method}', params=params) as response:
			if test:
				print(response)
			answer = await response.json()
		await session.close()
		return answer
	except:
		await session.close()
		if iteration < MNR:
			if test:
				print("[ERROR]")
			await asyncio.sleep(1)
			return await get(method, url, params, iteration + 1)
		else:
			return None


async def post(url: str = URL, method: str = "", params: dict = {}, iteration: int = 0) -> Optional[dict]:
	"""
	Asynchronous function for POST requests that accepts 
	url <url> and method <method> and parameters <params>
	"""

	session = aiohttp.ClientSession(
			json_serialize=ujson.dumps,
			trust_env = True, 
			connector=aiohttp.TCPConnector(verify_ssl=False)
	)

	try:
		async with session.post(f'{url}{method}', params=params) as response:
			answer = await response.json()
		await session.close()
		return answer
	except:
		await session.close()
		if iteration < MNR:
			await asyncio.sleep(1)
			return await post(method, url, params, iteration + 1)
		else:
			return None