from telethon import TelegramClient
from telethon.tl.types import User


async def sign_in_to_telegram(client: TelegramClient):
    phone = input('phone: ')
    login_token = await client.request_login_code(phone)

    code = input('code: ')
    user_or_token = await client.sign_in(login_token, code)

    if isinstance(user_or_token, User):
        return user_or_token

    # user_or_token is PasswordToken
    password_token = user_or_token

    import getpass
    password = getpass.getpass("password: ")
    user = await client.check_password(password_token, password)