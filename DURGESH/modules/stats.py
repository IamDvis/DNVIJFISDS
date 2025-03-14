from pyrogram import filters
from pyrogram.types import Message

from DURGESH import OWNER, dev
from DURGESH.database.chats import get_served_chats
from DURGESH.database.users import get_served_users
from pyrogram.types import InlineKeyboardMarkup
from DURGESH.modules.helpers import PNG_BTN


@dev.on_message(filters.command("stats") & filters.user(OWNER))
async def stats(cli: dev, message: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(
        f"""❖ ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛs ᴏғ {(await cli.get_me()).mention} ⏤͟͟͞͞★\n\n● ᴛᴏᴛᴀʟ ᴄʜᴀᴛs ➥ {chats}\n● ᴛᴏᴛᴀʟ ᴜsᴇʀs ➥ {users}""", reply_markup=InlineKeyboardMarkup(PNG_BTN),
    )
    
  
