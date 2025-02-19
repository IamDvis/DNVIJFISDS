
from DURGESH import app

import re
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@app.on_message(filters.text & filters.regex(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"))
async def auto_download_instagram_video(client, message):
    url = message.text
    a = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    try:
        response = requests.get(api_url)
        result = response.json()
        data = result["result"]
        
        if not result["error"]:
            video_url = data["url"]
            duration = data.get("duration", "N/A")
            quality = data.get("quality", "N/A")
            type = data.get("extension", "N/A")
            size = data.get("formattedSize", "N/A")
            
            # Create keyboard with Extract Audio button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Extract Audio 🎵", callback_data=f"extract_{video_url}")]
            ])
            
            caption = (
                f"**Dᴜʀᴀᴛɪᴏɴ :** {duration}\n"
                f"**Qᴜᴀʟɪᴛʏ :** {quality}\n"
                f"**Tʏᴘᴇ :** {type}\n"
                f"**Sɪᴢᴇ :** {size}"
            )
            await a.delete()
            await message.reply_video(video_url, caption=caption, reply_markup=keyboard)
        else:
            await a.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
    except Exception as e:
        await a.edit(f"Eʀʀᴏʀ: {str(e)}")

@app.on_callback_query(filters.regex("^extract_"))
async def extract_audio(client, callback_query):
    try:
        video_url = callback_query.data.replace("extract_", "")
        await callback_query.message.reply_text("Exᴛʀᴀᴄᴛɪɴɢ ᴀᴜᴅɪᴏ...")
        
        # Send as audio file
        await callback_query.message.reply_audio(
            video_url,
            title="Instagram Audio",
            performer="Instagram Reel"
        )
        await callback_query.answer("Audio extracted successfully!")
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
