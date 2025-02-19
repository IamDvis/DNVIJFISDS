import re
import os
import requests
import logging
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from DURGESH import app

@app.on_message(filters.text & filters.regex(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"))
async def auto_download_instagram_video(client, message):
    url = message.text.strip()
    a = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    try:
        logging.info(f"Requesting: {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("error") or "result" not in result:
            raise ValueError("Invalid API response")
        data = result["result"]
        video_url = data["url"]
        
        # Validate video URL
        head_response = requests.head(video_url, timeout=5)
        head_response.raise_for_status()

    except requests.exceptions.RequestException as e:
        err_msg = f"API Error: {e}"
        await a.edit(err_msg)
        return

    # Download video locally
    temp_video = "temp_video.mp4"
    try:
        with requests.get(video_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(temp_video, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        # Get file size
        size = os.path.getsize(temp_video)
        size_mb = round(size / (1024 * 1024), 2)
    except Exception as e:
        await a.edit(f"Video download failed: {e}")
        return
    finally:
        if os.path.exists(temp_video) is False:
            await a.edit("Video file not found")
            return

    # Generate caption
    duration = data.get("duration", "unknown")
    quality = data.get("quality", "unknown")
    file_type = data.get("extension", "unknown")
    caption = (
        f"**Dᴜʀᴀᴛɪᴏɴ :** {duration}\n"
        f"**Qᴜᴀʟɪᴛʏ :** {quality}\n"
        f"**Tʏᴘᴇ :** {file_type}\n"
        f"**Sɪᴢᴇ :** {size_mb} MB"
    )

    try:
        await message.reply_video(temp_video, caption=caption)
        await a.delete()
    except Exception as e:
        await a.edit(f"Failed to send video: {e}")
        return

    # Cleanup
    os.remove(temp_video)
