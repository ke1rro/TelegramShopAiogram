from aiogram.enums import ChatMemberStatus


def check_user_sub(chat_member) -> bool:
    if chat_member.status in [ChatMemberStatus.LEFT]:
        return False
    else:
        return True
