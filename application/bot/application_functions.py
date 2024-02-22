from app.models import Account, Chats, ChatsUser
from other_cmd import get_chat_name

async def register_user(user_id):
    user = Account.objects.filter(uid=user_id).first()
    if user is None:
        get_api = await Account.TempData.bot('users.get', {'user_ids': str(user_id)})
        if get_api is not None:
            get_api = get_api['response'][0]
            user = Account.objects.create(uid=get_api['id'], nickname=get_api['first_name'])
    return user


async def register_chat(event):
    peer_id = event['peer_id']
    chat = Chats.objects.filter(uid=peer_id).first()
    if chat is None:
        chat = Chats.objects.create(uid=peer_id)

    return chat


async def register_chat_user(user, chat):
    chat_user = ChatsUser.objects.filter(chat=chat, user=user).first()
    if chat_user is None:
        chat_user = ChatsUser.objects.create(chat=chat, user=user)

    return chat_user