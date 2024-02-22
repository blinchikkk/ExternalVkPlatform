from . import handler
from engine import console
from .vk.LongPoll import VK
from django.conf import settings
from datetime import datetime, timedelta
import os
import importlib
import re
import asyncio
import json
from .application_functions import register_user, register_chat, register_chat_user
from application.models import Account, Chats, ChatsUser, Logs
from other_cmd import remove_member, check_filter, remove_message
from application.bot.vk.RequestsToVK import post as vkPost


class VkBot:
    def __init__(self):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.start())

    async def start(self):
        await console.log('Инициализация VK...')
        self.vk = VK()

        await self.read_handlers()

        Chats.TempData.bot = self.vk.api
        Account.TempData.bot = self.vk.api
        ChatsUser.TempData.bot = self.vk.api

        
        @self.vk.responseHandler()
        async def responseHandler(update):
            if update['type'] == 'message_new' or update['type'] == 'message_event':
                if update['type'] == 'message_event':
                    event = {
                        'from_id': update['object']['user_id'],
                        'id': update['object'].get('conversation_message_id'),
                        'out': 0,
                        'attachments': [],
                        'conversation_message_id': update['object']['conversation_message_id'],
                        'fwd_messages': [],
                        'important': False,
                        'is_hidden': False,
                        'payload': update['object']['payload'],
                        'peer_id': update['object']['peer_id'],
                        'random_id': 0,
                        'text': ' ',
                        'event_id': update['object']['event_id'],
                        'type': 'callback'
                    }
                else:
                    event = update['object']['message']
                    
                if event['from_id'] > 0:
                    user = await register_user(event['from_id'])

                    action = event.get('action', None)
                    Logs.objects.create(
                        user=user, message=event['text'], time=datetime.now())
                    if action is None:
                        get_payload = event.get('payload', None)
                        payload_command = None

                        if get_payload is not None and get_payload != '':
                            if type(event['payload']) == dict:
                                payload_command_json = event['payload']
                            else:
                                payload_command_json = json.loads(
                                    event['payload'])

                            if type(payload_command) != str:
                                payload_command = payload_command_json.get(
                                    'command', None)
                                if payload_command is None:
                                    payload_command = payload_command_json.get(
                                        'payload', None)

                        processed_name = event['text'].lower().strip()
                        processed_name = processed_name.replace(
                            f'[club{settings.GROUP_ID}|{processed_name[processed_name.find("|") + 1: processed_name.find("]")]}]', '').strip()
                        processed_name = re.sub(
                            r'^[^а-яА-ЯёЁ]\s', '', processed_name)
                        args = re.split(r'\s+', processed_name)

                        no_cmd = f'❌ {user.mention()}, команда не найдена!' \
                            f'\n\n❓ Задать вопрос › Репорт [текст].'
                        err_msg = f'❌ {user.mention()}, произошла ошибка!'

                        if event['peer_id'] > 2000000000:
                            chat = await register_chat(event)
                            chat_user = await register_chat_user(user, chat)

                            chat.messages += 1
                            chat.save()

                            if chat_user.is_owner is False:
                                chat_user.is_owner = True
                                chat_user.is_admin = True
                                chat_user.is_moder = True
                                chat_user.save()

                                await chat_user.reply(f'ℹ [id{user.uid}|Ваши] права были обновлены!')
                            # Проверка на мут
                            if datetime.now() > chat_user.mute_time:
                                mute_user = False
                            else:
                                mute_user = True
                                get_remove_message = await remove_message(bot=self.vk, chat=chat, message=event)
                                if get_remove_message[0] is not None:
                                    if get_remove_message[0] is False:
                                        if get_remove_message[1] == 15:
                                            chat_user.mute_time = datetime.now() - timedelta(minutes=15)
                                            chat_user.save()

                            mention_text = args[0][3:].split('|')[0]
                            if mention_text.isdigit():
                                acc_data = Account.objects.filter(
                                    uid=mention_text)
                                if acc_data.count() > 0:
                                    if ChatsUser.objects.filter(chat=chat, user=acc_data.last(), mention=False).count() > 0:
                                        mention_status = False
                                        if chat_user.warns + 1 > 2:
                                            send_remove_member = await remove_member(bot=self.vk, chat=chat,
                                                                                     remove_id=user.uid)
                                            if send_remove_member[0]:
                                                await chat.reply(
                                                    f'ℹ {user.mention()}, [id{user.uid}|пользователю] было выдано предупреждение [{chat_user.warns + 1}/3], за упоминание пользователя, которого нельзя упоминать, и был исключён!')
                                                chat_user.warns = 0
                                                chat_user.save()
                                            else:
                                                if send_remove_member[1] == 15:
                                                    await chat.reply(
                                                        f'ℹ {user.mention()}, [id{user.uid}|пользователю] было выдано предупреждение [{chat_user.warns}/3], за упоминание пользователя, которого нельзя упоминать, и исключить его из этой беседы сейчас нельзя!\n\n* Для начала попробуйте понизить права участника беседы и повторите попытку.')
                                                else:
                                                    await chat.reply(
                                                        f'ℹ {user.mention()}, [id{user.uid}|пользователю] было выдано предупреждение [{chat_user.warns}/3], за упоминание пользователя, которого нельзя упоминать, и исключить его из этой беседы сейчас нельзя! Напишите нам в поддержку, и мы решим эту проблему вместе!')
                                        else:
                                            chat_user.warns += 1
                                            chat_user.save()

                                            await chat.reply(f'ℹ {user.mention()}, [id{user.uid}|пользователю] было выдано предупреждение [{chat_user.warns}/3] за упоминание пользователя, которого нельзя упоминать!\n\n* Как только у Вас будет 3-е предупреждение, Вы будете автоматически исключены из беседы!')
                                    else:
                                        mention_status = True
                                else:
                                    mention_status = True
                            else:
                                mention_status = True
                        else:
                            chat, chat_user = None, None
                            mute_user, mention_status = False, True

                            if user.wrote_personal is False:
                                user.wrote_personal = True
                                user.save()

                        if mute_user is False and mention_status is True:
                            user.messages_count += 1
                            user.last_peer_id = event['peer_id']
                            user.online_time = datetime.now()
                            user.save()

                            if user.ban is False:
                                if payload_command is None:
                                    get_check_filter = await check_filter(chat=chat, bot=self.vk,
                                                                          args=args, chat_user=chat_user)
                                    if get_check_filter:
                                        for command in handler.commands:
                                            if (not command.with_args and command.name in ['', processed_name]) or (command.with_args and command.name in ['', args[0], " ".join(x for x in args[0:len(command.name.split())]) if len(args) >= len(command.name.split()) else ""]):
                                                if not await command.handle(event, args, self.vk, user, chat, chat_user):
                                                    await user.reply(err_msg)
                                                break
                                        else:
                                            if chat is None:
                                                await user.reply(no_cmd, keyboard=[[{"label": "🗂 Помощь", "type": "text", "color": "secondary", "payload": {"payload": "help"}}]], inline=True)
                                    else:
                                        await remove_member(bot=self.vk, chat=chat, remove_id=chat_user.user.uid)
                                else:
                                    payload_command = re.split(
                                        r'\s+', payload_command)
                                    for payload in handler.payloads:
                                        if payload.name == payload_command[0]:
                                            if event.get("type") == 'callback':
                                                if event['payload']['personal'] and user.uid != payload_command[-1]:
                                                    await vkPost(method='messages.sendMessageEventAnswer', params={
                                                        'access_token': settings.BOT_TOKEN,
                                                        'event_id': event['event_id'],
                                                        'user_id': event['from_id'],
                                                        'peer_id': event['peer_id'],
                                                        'event_data': json.dumps({'type': 'show_snackbar', 'text': '❌ Ты не можешь использовать эту кнопку т.к она тебе не принадлежит'}),
                                                        'v': '5.131'
                                                    })
                                                    break
                                            if not await payload.handle(event, payload_command, self.vk, user, chat, chat_user):
                                                await user.reply(err_msg)
                                            if event.get("type") == 'callback':
                                                await vkPost(method='messages.sendMessageEventAnswer', params={
                                                    'access_token': settings.BOT_TOKEN,
                                                    'event_id': event['event_id'],
                                                    'user_id': event['from_id'],
                                                    'peer_id': event['peer_id'],
                                                    'v': '5.131'
                                                })
                                            break
                                    else:
                                        if chat is None:
                                            await user.reply(no_cmd, keyboard=[[{"label": "🗂 Помощь", "type": "text", "color": "secondary", "payload": {"payload": "help"}}]], inline=True)
                    else:
                        if action['type'] == 'chat_invite_user':
                            GROUP_ID = os.environ['GROUP_ID']
                            BOT_NAME = os.environ['BOT_NAME']
                            event = update['object']['message']

                            chat = await register_chat(event=event)

                            if action['member_id'] < 0:
                                if action['member_id'] == -int(GROUP_ID):
                                    await chat.reply(
                                        f'👋🏻 Привет всем участникам беседы. Я — игровой бот [public{GROUP_ID}|{BOT_NAME}]!',
                                        keyboard=main_keyboard,
                                        attachment='photo209037193_457239025')
                            else:
                                await chat.reply(await chat_user_add(uid=action['member_id']), keyboard=user_join_group_keyboard, inline=True)
                                member_user = await register_user(user_id=action['member_id'])
                                chat = await register_chat(event=event)

            elif update['type'] == 'group_join':
                event = update['object']
                acc_data = await register_user(event['user_id'])

        await self.vk.LongPoll()

    async def read_handlers(self):
        PLATFORM_VERSION = "0.1 BETA"
        await console.log(f'Запуск FREEZINGBOT (v.{PLATFORM_VERSION})...')
        await console.log('Этот сервер предназначен для обработки событий от VK!')
        await console.log('Инициализация команд...')

        for root, dirs, files in os.walk('app/bot/commands'):
            check_extension = filter(lambda x: x.endswith('.py'), files)
            for command in check_extension:
                path = os.path.join(root, command)
                spec = importlib.util.spec_from_file_location(
                    command, os.path.abspath(path))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

        await console.log('Бот готов к работе!')