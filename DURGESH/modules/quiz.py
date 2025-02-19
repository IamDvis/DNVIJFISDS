import random
import asyncio
import requests
from pyrogram import filters
from pyrogram.enums import PollType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from DURGESH import app

quiz_loops = {}
active_polls = {}

async def fetch_quiz_question():
    categories = [9, 17, 18, 20, 21, 27]
    url = f"https://opentdb.com/api.php?amount=1&category={random.choice(categories)}&type=multiple"
    response = requests.get(url).json()
    data = response["results"][0]
    return data["question"], data["incorrect_answers"] + [data["correct_answer"]], data["correct_answer"]

async def send_quiz_poll(chat_id, user_id, interval):
    question, all_answers, correct = await fetch_quiz_question()
    random.shuffle(all_answers)
    cid = all_answers.index(correct)
    
    if user_id in active_polls:
        try:
            await app.delete_messages(chat_id=chat_id, message_ids=active_polls[user_id])
        except:
            pass
    
    poll = await app.send_poll(
        chat_id=chat_id,
        question=question,
        options=all_answers,
        is_anonymous=False,
        type=PollType.QUIZ,
        correct_option_id=cid,
        open_period=interval
    )
    if poll:
        active_polls[user_id] = poll.id

@app.on_message(filters.command(["quiz"], prefixes=["/", "!", ""]))
async def quiz_info(_, message):
    await message.reply_text(
        "**Welcome to the Quiz Bot!**\n\n"
        "Here is how it works:\n"
        "1. Use `/quizon` to start a quiz loop. After starting, choose a time interval for the quiz.\n"
        "2. Intervals available: 30 seconds, 1 minute, 5 minutes, or 10 minutes.\n"
        "3. Quizzes will appear at the chosen interval with a time limit.\n"
        "4. Stop the loop anytime with `/quizoff`.\n\n"
        "**Commands**:\n"
        "• `/quizon` - Start the quiz loop\n"
        "• `/quizoff` - Stop the quiz loop\n\n"
        "Enjoy the quizzes! 🎉"
    )

@app.on_message(filters.command(["quizon"], prefixes=["/", "!", ""]))
async def quiz_on(_, message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("30s", callback_data="30_sec"), InlineKeyboardButton("1min", callback_data="1_min")],
            [InlineKeyboardButton("5min", callback_data="5_min"), InlineKeyboardButton("10min", callback_data="10_min")],
        ]
    )
    await message.reply_text(
        "**Choose quiz frequency:**\n\n"
        "- 🕒 30s\n"
        "- ⏣ 1 min\n"
        "- ⏣ 5 mins\n"
        "- ⏣ 10 mins\n\n"
        "Stop the quiz loop at any time with `/quizoff`.",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^\d+_sec$|^\d+_min$"))
async def start_quiz_loop(_, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if user_id in quiz_loops:
        await callback_query.answer("Quiz loop is already running!", show_alert=True)
        return
    
    await callback_query.message.delete()
    
    data = callback_query.data
    intervals = {
        "30_sec": 30,
        "1_min": 60,
        "5_min": 300,
        "10_min": 600
    }
    interval = intervals.get(data)
    interval_text = {
        "30_sec": "30 seconds",
        "1_min": "1 minute",
        "5_min": "5 minutes",
        "10_min": "10 minutes"
    }[data]
    
    quiz_loops[user_id] = True
    await callback_query.message.reply(f"✅ Quizs started! New quizzes every {interval_text}.")

    async def quiz_loop():
        while quiz_loops.get(user_id, False):
            await send_quiz_poll(chat_id, user_id, interval)
            await asyncio.sleep(interval)
    
    asyncio.create_task(quiz_loop())

@app.on_message(filters.command(["quizoff"], prefixes=["/", "!", ""]))
async def stop_quiz(_, message):
    user_id = message.from_user.id
    
    if user_id not in quiz_loops:
        await message.reply("No quiz loop is running.")
    else:
        del quiz_loops[user_id]
        await message.reply("⛔ Quiz loop stopped.")
        if user_id in active_polls:
            try:
                await app.delete_messages(message.chat.id, active_polls.pop(user_id))
            except:
                pass
