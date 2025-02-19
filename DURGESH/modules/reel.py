import re
import requests
import logging
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from DURGESH import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.on_message(filters.text & filters.regex(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"))
async def auto_download_instagram_video(client, message):
    url = message.text
    a = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    try:
        logging.info(f"Sending request to: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        logging.info(f"API Response: {result}")
        data = result["result"]
    except requests.exceptions.RequestException as e:
        err_message = f"Network Eʀʀᴏʀ: {e}"
        logging.error(err_message)
        try:
            await a.edit(err_message)
        except Exception as edit_error:
            logging.error(f"Edit error: {edit_error}")
            await message.reply_text(err_message)
        return
    except (KeyError, ValueError) as e:
        err_message = f"Data processing Eʀʀᴏʀ: {e}"
        logging.error(err_message)
        try:
            await a.edit(err_message)
        except Exception as edit_error:
            logging.error(f"Edit error: {edit_error}")
            await message.reply_text(err_message)
        return
    except Exception as e:
        err_message = f"Unknown Eʀʀᴏʀ: {e}"
        logging.error(err_message)
        try:
            await a.edit(err_message)
        except Exception as edit_error:
            logging.error(f"Edit error: {edit_error}")
            await message.reply_text(err_message)
        return

    if not result["error"]:
        video_url = data["url"]
        duration = data["duration"]
        quality = data["quality"]
        type = data["extension"]
        size = data["formattedSize"]
        audio_url = data.get("audio_url")  # Use .get() to avoid KeyError if audio_url is missing
        caption = (
            f"**Dᴜʀᴀᴛɪᴏɴ :** {duration}\n"
            f"**Qᴜᴀʟɪᴛʏ :** {quality}\n"
            f"**Tʏᴘᴇ :** {type}\n"
            f"**Sɪᴢᴇ :** {size}"
        )
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Extract Audio", url=audio_url)] if audio_url else []
            ]
        )
        await a.delete()
        await message.reply_video(video_url, caption=caption, reply_markup=buttons)
    else:
        try:
            await a.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
        except Exception:
            await message.reply_text("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
