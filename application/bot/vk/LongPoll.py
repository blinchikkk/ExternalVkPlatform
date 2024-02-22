from django.conf import settings
from typing import Optional, Callable
from .RequestsToVK import post as vkPost, get as vkGet


class VK:
	"""VK class"""

	def __init__(self):
		self.user_token: Optional[str] = settings.USER_TOKEN if settings.USER_TOKEN else None
		self.__token: Optional[str] = settings.BOT_TOKEN if settings.BOT_TOKEN else None
		self.__group_id: Optional[int] = settings.GROUP_ID if settings.GROUP_ID else None
		self.__response_handler: Optional[Callable] = None
		self.__wait: int = 25

		if self.__token is None:
			raise Exception("The token was entered incorrectly")

		if self.__group_id is None:
			raise Exception("The group_id was entered incorrectly")


	def responseHandler(self, **kwargs):
		"""Decorator for defining the handler function"""

		def wrapper(func):
			self.__response_handler = func
		return wrapper


	async def api(self, method: str = "", params: dict = {}, user: bool = False) -> Optional[dict]:
		"""Function for easy access to the VK API"""

		if user:
			params.update({'group_id': self.__group_id, 'v': '5.131', 'access_token': self.user_token})
		else:
			params.update({'group_id': self.__group_id, 'v': '5.131', 'access_token': self.__token})
		return await vkPost(method = method, params = params)


	async def __getLongPollServer(self) -> dict:
		"""Function for getting data from the getLongPollServer method"""

		response: Optional[dict] = await self.api("groups.getLongPollServer")

		if response is None:
			raise Exception("The getLongPollServer function could not get the data, do you have an internet connection?")

		if response.get("error") is not None:
			raise Exception("the getLongPollServer function could not get the data, did you enter the token and the group id correctly?")

		return response['response'].values()


	async def LongPoll(self):
		"""A function that listens to the LongPoll server"""

		key, server, ts = await self.__getLongPollServer()

		while True:
			if ts is None:
				key, server, ts = await self.__getLongPollServer()

			response: dict = await vkGet(f'{server}?act=a_check&key={key}&ts={ts}&wait={self.__wait}')

			if response.get('failed') is not None:
				if response["failed"] == 1:
					ts = response["ts"]
				elif response["failed"] in [2, 3]:
					ts = None
				continue

			ts = response['ts']

			for event in response['updates']:
				await self.__response_handler(event)