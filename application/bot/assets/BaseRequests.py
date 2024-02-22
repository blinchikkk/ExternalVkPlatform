import traceback, sys


class Command:
    def __init__(self, **kwargs):
        if not kwargs.keys() & {'name', 'handler', 'admin'}:
            raise Exception('Not enough arguments to create command object')
        self.name = kwargs['name'].lower()
        self.__handler = kwargs['handler']
        self.admin = kwargs['admin']
        self.game_chat = kwargs['game_chat']
        self.only_chat = kwargs['only_chat']
        self.is_moder = kwargs['is_moder']
        self.is_admin = kwargs['is_admin']
        self.is_owner = kwargs['is_owner']
        self.chat_activation = kwargs['chat_activation']
        self.with_args = kwargs['with_args']

    async def handle(self, event, args, api, user, chat, chat_user):
        try:
            if self.admin is True and user.admin is False:
                return True
            elif self.only_chat is True and chat is None:
                await user.reply(text=f'❌ {user.mention()}, эта команда работает только в беседах!')
                return True
            elif self.chat_activation is True and chat.activation is False:
                await chat.reply(text=f'❌ {user.mention()}, бот в этой беседе не работает!\n'
                                      f'\n* Выдайте боту права администратора, и напишите команду - /активировать',
                                 keyboard=[[{"label": "🔰 Активировать", "type": "text", "color": "secondary",
                                             "payload": {"payload": "activation"}}]], inline=True)
                return True
            elif self.is_moder is True and chat_user.is_moder is False:
                await chat_user.reply(text=f'❌ {user.mention()}, у вас нет прав на исполнения этой команды!')
                return True
            elif self.is_admin is True and chat_user.is_admin is False:
                await chat_user.reply(text=f'❌ {user.mention()}, у вас нет прав на исполнения этой команды!')
                return True
            elif self.is_owner is True and chat_user.is_owner is False:
                await chat_user.reply(text=f'❌ {user.mention()}, у вас нет прав на исполнения этой команды!')
                return True
            elif chat is not None:
                if self.game_chat is True and chat.games is False:
                    return True
            await self.__handler(event, args, api, user, chat, chat_user)
            return True
        except Exception:
            ex_type, ex, tb = sys.exc_info()
            print(ex, traceback.format_tb(tb))
            return False


class Payload:
    def __init__(self, **kwargs):
        if not kwargs.keys() & {'name', 'handler', 'admin'}:
            raise Exception('Not enough arguments to create command object')
        self.name = kwargs['name'].lower()
        self.__handler = kwargs['handler']
        self.admin = kwargs['admin']
        self.game_chat = kwargs['game_chat']
        self.only_chat = kwargs['only_chat']
        self.chat_activation = kwargs['chat_activation']
        self.is_moder = kwargs['is_moder']
        self.is_admin = kwargs['is_admin']
        self.is_owner = kwargs['is_owner']
        self.with_args = kwargs['with_args']

    async def handle(self, event, args, api, user, chat, chat_user):
        try:
            if self.only_chat is True and chat is None:
                await user.reply(text=f'❌ {user.mention()}, эта команда работает только в беседах!')
                return True
            elif self.chat_activation is True and chat.activation is False:
                await chat.reply(text=f'❌ {user.mention()}, бот в этой беседе не работает!\n'
                                      f'\n* Выдайте боту права администратора, и напишите команду - /активировать',
                                 keyboard=[[{"label": "🔰 Активировать", "type": "text", "color": "secondary",
                                             "payload": {"payload": "activation"}}]], inline=True)
                return True
            elif self.is_moder is True and chat_user.is_moder is False:
                await chat_user.reply(text=f'❌ {user.mention()}, у вас нет прав на исполнение этой команды!')
                return True
            elif self.is_admin is True and chat_user.is_admin is False:
                await chat_user.reply(text=f'❌ {user.mention()}, у вас нет прав на исполнение этой команды!')
                return True
            elif self.is_owner is True and chat_user.is_owner is False:
                await chat_user.reply(text=f'❌ {user.mention()}, у вас нет прав на исполнение этой команды!')
                return True
            elif chat is not None:
                if self.game_chat is True and chat.games is False:
                    return True
            await self.__handler(event, args, api, user, chat, chat_user)
            return True
        except Exception:
            ex_type, ex, tb = sys.exc_info()
            print(ex, traceback.format_tb(tb))
            return False


class Callback:
    def __init__(self, **kwargs):
        if not kwargs.keys() & {'name', 'handler', 'admin'}:
            raise Exception('Not enough arguments to create command object')
        self.name = kwargs['name'].lower()
        self.__handler = kwargs['handler']
        self.admin = kwargs['admin']
        self.with_args = kwargs['with_args']

    async def handle(self, event, args, api, user):
        try:
            await self.__handler(event, args, api, user)
            return True
        except Exception:
            ex_type, ex, tb = sys.exc_info()
            print(ex, traceback.format_tb(tb))
            return False