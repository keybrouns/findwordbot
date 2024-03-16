from keep_alive import keep_alive
from aiogram import types, Dispatcher, executor, Bot
from words import words
import random
import os

keep_alive()

supbot = Bot(token=os.environ.get('SUPTOKEN'))
bot = Bot(token=os.environ.get('TOKEN'))
dp = Dispatcher(bot)



users_sessions = {}

# isplaying = False
# word = None
# word_letters = None
# user_letters = None

async def display(user_letters,word):
    display_letter = ""
    for letter in word:
        if letter in user_letters:
            display_letter += letter
        else:
            display_letter += "-"
    return display_letter

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    global users_sessions
    # global isplaying
    users_sessions[message.from_user.id] = {'isplaying': False, 'word': None, 'word_letters': None, 'user_letters': None, 'letter': None}
    # isplaying = False
    await message.answer("👋 Welcome! To play send me a command /play")
    # await message.answer("for more info /help")

    await supbot.send_message(chat_id=os.environ.get('SUPID'), text=f"#joined 👤\n\nid: {message.from_user.id}\nfull name: {message.from_user.full_name}\nusername: @{message.from_user.username}\nlang code: {message.from_user.language_code}")

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer("ℹ️ With this bot you can play a find word game!\n/play - to start a game \n/giveup - to give up", parse_mode='html')

@dp.message_handler(commands=['giveup'])
async def cmd_giveup(message: types.Message):
    global users_sessions
    userid = message.from_user.id
    if userid not in users_sessions:
        await message.answer("please send me /start to start a bot")
    else:
        # print(users_sessions[message.from_user.id]['isplaying'])
        if users_sessions[message.from_user.id]['isplaying']:
            await message.answer(f"😬 The word was {users_sessions[message.from_user.id]['word']}, enter /play to play again.")
            users_sessions[message.from_user.id]['isplaying'] = False
            users_sessions[message.from_user.id]['word'] = None
            users_sessions[message.from_user.id]['word_letters'] = None
            users_sessions[message.from_user.id]['user_letters'] = None
            users_sessions[message.from_user.id]['letter'] = None
        elif not users_sessions[message.from_user.id]['isplaying']:
            await message.answer("🤧 You didn't start a game, to start a game enter /play")



@dp.message_handler(commands=['play'])
async def cmd_play(message: types.Message):
    global users_sessions

    userid = message.from_user.id
    if userid not in users_sessions:
        await message.answer("please send me /start to start a bot")
    else:
        if not users_sessions[message.from_user.id]['isplaying']:
            users_sessions[message.from_user.id]['isplaying'] = True
            
            users_sessions[message.from_user.id]['word'] = random.choice(words).upper()
            users_sessions[message.from_user.id]['word_letters'] = set(users_sessions[message.from_user.id]['word'])
            users_sessions[message.from_user.id]['user_letters'] = ''

            await supbot.send_message(chat_id=os.environ.get('SUPID'), text=f"#playing 🎮\n\nid: {message.from_user.id}\nfull name: {message.from_user.full_name}\nusername: @{message.from_user.username}\nlang code: {message.from_user.language_code}\n\nword: {users_sessions[message.from_user.id]['word']}")

            # print(word)
            await message.answer("🚀 Let's start!")
            await bot.send_message(chat_id=message.chat.id, text=f"🧐 I've thought a word <b>with {len(users_sessions[message.from_user.id]['word'])} letters</b>, can you guess it?", parse_mode='html')
            
            await bot.send_message(chat_id=message.chat.id, text=f"Letters you have entered so far: \n{users_sessions[message.from_user.id]['user_letters']}\n\n{await display(users_sessions[message.from_user.id]['user_letters'],users_sessions[message.from_user.id]['word'])}\n\nEnter a letter: ")
        elif users_sessions[message.from_user.id]['isplaying']:
            await message.answer("Please first complete previous game or enter /giveup to cancel it")

@dp.message_handler()
async def letter_get(message: types.Message):
    global users_sessions
    userid = message.from_user.id
    if userid not in users_sessions:
        await message.answer("please send me /start to start a bot")
    else:
        if not users_sessions[message.from_user.id]['isplaying']:
            await message.answer("👉 Enter /play to start the game")
        elif users_sessions[message.from_user.id]['isplaying']:
            if users_sessions[message.from_user.id]['word_letters']:
                users_sessions[message.from_user.id]['letter'] = message.text.upper()
                if len(users_sessions[message.from_user.id]['letter']) > 1:
                    await message.answer(f"❕ Please enter <b>one</b> letter at a time", parse_mode='html')
                else:
                    if users_sessions[message.from_user.id]['letter'] in users_sessions[message.from_user.id]['user_letters']:
                        await message.answer(f"❕ You have entered this letter please enter another")
                    elif users_sessions[message.from_user.id]['letter'] in users_sessions[message.from_user.id]['word']:
                        users_sessions[message.from_user.id]['user_letters'] += users_sessions[message.from_user.id]['letter']
                        users_sessions[message.from_user.id]['word_letters'].remove(users_sessions[message.from_user.id]['letter'])
                        await message.answer(f"✅ You found {users_sessions[message.from_user.id]['letter']} letter")
                        await bot.send_message(chat_id=message.chat.id, text=f"Letters you have entered so far: \n [ {' '.join(users_sessions[message.from_user.id]['user_letters'])} ]\n\n{await display(users_sessions[message.from_user.id]['user_letters'],users_sessions[message.from_user.id]['word'])}\n\nEnter a letter: ")
                    else:
                        users_sessions[message.from_user.id]['user_letters'] += users_sessions[message.from_user.id]['letter']
                        await message.answer(f"❌ There is no such letter")
                        await bot.send_message(chat_id=message.chat.id, text=f"Letters you have entered so far: \n [ {' '.join(users_sessions[message.from_user.id]['user_letters'])} ]\n\n{await display(users_sessions[message.from_user.id]['user_letters'],users_sessions[message.from_user.id]['word'])}\n\nEnter a letter: ")
            if not users_sessions[message.from_user.id]['word_letters']:
                await message.answer(f"🎉 Congrats! You found \"{users_sessions[message.from_user.id]['word']}\" word in {len(users_sessions[message.from_user.id]['user_letters'])} attempts.", parse_mode='html')
                users_sessions[message.from_user.id] = {'isplaying': False, 'word': None, 'word_letters': None, 'user_letters': None, 'letter': None}


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
