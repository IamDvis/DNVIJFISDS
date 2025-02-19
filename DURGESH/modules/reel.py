
from DURGESH import app


import re
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytube import YouTube
import os

# Create downloads directory if not exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')

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
            
            # Store URL for later use
            if not hasattr(app, 'url_store'):
                app.url_store = {}
            app.url_store[str(message.id)] = video_url
            
            caption = (
                f"**Dᴜʀᴀᴛɪᴏɴ:** {data['duration']}\n"
                f"**Qᴜᴀʟɪᴛʏ:** {data['quality']}\n"
                f"**Tʏᴘᴇ:** {data['extension']}\n"
                f"**Sɪᴢᴇ:** {data['formattedSize']}"
            )
            await a.delete()
            await message.reply_video(video_url, caption=caption, reply_markup=keyboard)
    except Exception as e:
        await a.edit(f"Error: {str(e)}")

@app.on_callback_query(filters.regex("^audio_"))
async def extract_audio(client, callback_query):
    message_id = callback_query.data.split("_")[1]
    video_url = app.url_store.get(str(message_id))
    
    if not video_url:
        await callback_query.answer("Video URL expired. Try again.", show_alert=True)
        return

    status_msg = await callback_query.message.reply_text("Downloading audio...")

    try:
        # Use pytube to download the best audio stream
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()

        if not audio_stream:
            await status_msg.edit("No audio stream found.")
            return

        output_path = f"downloads/audio_{message_id}.mp3"
        audio_stream.download(filename=output_path)

        # Send the audio file
        await callback_query.message.reply_audio(
            output_path,
            title="Instagram Audio",
            performer="Instagram Reel"
        )

        # Cleanup
        os.remove(output_path)
        del app.url_store[str(message_id)]
        await status_msg.delete()
        await callback_query.answer("Audio downloaded successfully!")

    except Exception as e:
        await status_msg.edit(f"Error extracting audio: {str(e)}")
