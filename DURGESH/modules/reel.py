
from DURGESH import app
import re
import requests
import yt_dlp
import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Add yt-dlp configuration
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(title)s.%(ext)s'
}

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
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Download Audio 🎵", callback_data=f"audio_{message.id}")]
            ])
            
            caption = (
                f"**Dᴜʀᴀᴛɪᴏɴ:** {data.get('duration', 'N/A')}\n"
                f"**Qᴜᴀʟɪᴛʏ:** {data.get('quality', 'N/A')}\n"
                f"**Tʏᴘᴇ:** {data.get('extension', 'N/A')}"
            )
            
            # Store video URL for callback
            if not hasattr(app, '_video_urls'):
                app._video_urls = {}
            app._video_urls[str(message.id)] = video_url
            
            await a.delete()
            await message.reply_video(video_url, caption=caption, reply_markup=keyboard)
            
    except Exception as e:
        await a.edit(f"Error: {str(e)}")

@app.on_callback_query(filters.regex("^audio_"))
async def download_audio(client, callback_query):
    try:
        message_id = callback_query.data.split("_")[1]
        video_url = app._video_urls.get(message_id)
        
        if not video_url:
            await callback_query.answer("Video URL expired. Please try again.", show_alert=True)
            return
            
        await callback_query.message.reply_text("Downloading audio...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            audio_path = f"downloads/{info['title']}.mp3"
            
            # Send audio file
            await callback_query.message.reply_audio(
                audio_path,
                title=info['title'],
                performer="Instagram Audio"
            )
            
            # Clean up
            os.remove(audio_path)
            del app._video_urls[message_id]
            
        await callback_query.answer("Audio downloaded successfully!")
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
