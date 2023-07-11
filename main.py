import configparser
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from sources.parsing import Parsing
from sources.algorithms import TextPrepare, Wordcloud, Summary, Morphemes, MessagesCount
from sources.database_api import DataBase

from encrypt.vernam import Vernam

config = configparser.ConfigParser()
config.read('config.ini')
bot_config = Bot(config['BOT']['token'])
bot = Dispatcher(bot_config, storage=MemoryStorage())

parsing = Parsing()
text_prepare = TextPrepare()
word_cloud = Wordcloud()
summary = Summary()
morphemes = Morphemes()
messages_count = MessagesCount()
vernam = Vernam()
db = DataBase()


with open('messages/welcome') as file:
    WELCOME = file.read()

with open('messages/help_1') as file:
    HELP_1 = file.read()

with open('messages/help_2') as file:
    HELP_2 = file.read()

with open('messages/config_bot') as file:
    CONFIG_BOT = file.read()

with open('messages/config_bot_again') as file:
    CONFIG_BOT_AGAIN = file.read()

with open('messages/date_min') as file:
    DATE_MIN = file.read()

with open('messages/date_max') as file:
    DATE_MAX = file.read()

with open('messages/parsing') as file:
    PARSING = file.read()

with open('messages/info_pos') as file:
    INFO_POS = file.read()

with open('messages/unknown_msg') as file:
    UNKNOWN_MSG = file.read()


class ConfigForm(StatesGroup):
    waiting_chat_name = State()
    waiting_date_min = State()
    waiting_date_max = State()
    completed = State()


class DecryptForm(StatesGroup):
    waiting_code = State()
    waiting_key = State()
    completed = State()


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await message.answer(WELCOME)


@bot.message_handler(commands=['help'])
async def send_help(message):
    await message.answer(HELP_1)
    await message.answer(HELP_2)

@bot.message_handler(commands=['help'], state=ConfigForm.completed)
async def send_help(message, state):
    await message.answer(HELP_1)
    await message.answer(HELP_2)


@bot.message_handler(commands=['config'])
async def set_bot_config(message):
    await message.answer(CONFIG_BOT)
    await ConfigForm.waiting_chat_name.set()

@bot.message_handler(commands=['config'], state=ConfigForm.completed)
async def set_bot_config_again(message, state):
    await state.reset_state()
    await message.answer(CONFIG_BOT_AGAIN)
    await ConfigForm.waiting_chat_name.set()


@bot.message_handler(state=ConfigForm.waiting_chat_name)
async def waiting_chat_name(message, state):
    chat_name = message.text
    if await parsing.chat_exist(chat_name):
        await state.update_data(chat_name=chat_name)
        await message.answer(DATE_MIN, parse_mode='Markdown')
        await ConfigForm.waiting_date_min.set()
    else:
        await state.reset_state()
        await message.answer('Ошибка при поиске чата.\nПопробуйте ещё раз: /config')


@bot.message_handler(state=ConfigForm.waiting_date_min)
async def waiting_date_min(message, state):
    date_min = message.text
    if parsing.check_format_data(date_min):
        await state.update_data(date_min=date_min)
        await message.answer(DATE_MAX, parse_mode='Markdown')
        await ConfigForm.waiting_date_max.set()
    else:
        await state.reset_state()
        await message.answer('Некорректный формат\nПопробуйте ещё раз: /config')


@bot.message_handler(state=ConfigForm.waiting_date_max)
async def waiting_date_max(message, state):
    date_max = message.text
    if parsing.check_format_data(date_max):
        await state.update_data(date_max=date_max)
        await message.answer(PARSING)
        chat_info = await state.get_data()
        try:
            await parsing.parse(chat_info)
            if len(parsing.get_df()) == 0:
                raise ValueError
            
            text_prepare.config(parsing.get_df())
            text_prepare.prepare()

            await message.answer('Настройка завершена! Теперь можете выбрать команду.')
            await ConfigForm.completed.set()
        except:
            await state.reset_state()
            await message.answer('Ошибка парсинга\nПопробуйте ещё раз: /config')
    else:
        await state.reset_state()
        await message.answer('Некорректный формат\nПопробуйте ещё раз: /config')


@bot.message_handler(commands=['wordcloud'], state=ConfigForm.completed)
async def wordcloud_command(message, state):
    await message.answer('Уже создаю облако слов!')
    word_cloud.create(text_prepare.keyword_with_audio)
    with open('media/cloud.png', 'rb') as photo:
        await message.answer_photo(photo)
    word_cloud.delete()
    

@bot.message_handler(commands=['summary'], state=ConfigForm.completed)
async def summary_command(message, state):
    await message.answer('Уже выделяю главное!')
    result = summary.create(text_prepare.doc, text_prepare.keyword)

    if len(result) > 4096:
        for x in range(0, len(result), 4096):
            await message.answer(result[x:x+4096])
    else:
        await message.answer(result)


@bot.message_handler(commands=['morphemes'], state=ConfigForm.completed)
async def morphemes_command(message, state):
    await message.answer('Уже провожу анализ по частям речи!')
    morphemes.create(text_prepare.doc_with_audio)
    with open('media/morphemes.png', 'rb') as photo:
        await message.answer_photo(photo)
    await message.answer(INFO_POS)
    morphemes.delete()


@bot.message_handler(commands=['count'], state=ConfigForm.completed)
async def count_command(message, state):
    await message.answer('Считаю сообщения!')
    messages_count.create(parsing.get_df())
    with open('media/dates.png', 'rb') as photo:
        await message.answer_photo(photo)
    messages_count.delete()


@bot.message_handler(commands=['encrypt'], state=ConfigForm.completed)
async def encrypt_command(message, state):
    await message.answer('Шифрую и сохраняю сообщения!')
    df = parsing.get_df()

    text = ''
    for i, msg in df.iterrows():
        if msg['text'] != None:
            text += msg['text'] + ' '
    
    key = vernam.genetate_key(10)
    text_enctypted = vernam.encrypt(text, key)
    code = db.add_message(text_enctypted)
    
    await message.answer(f'Сообщениие сохранено.\nКод сообщения: `{code}`\nШифр: `{key}`', parse_mode='Markdown')


@bot.message_handler(commands=['decrypt'], state=ConfigForm.completed)
async def decrypt_command(message, state):
    await message.answer('Введите код сообщения')
    await DecryptForm.waiting_code.set()


@bot.message_handler(state=DecryptForm.waiting_code)
async def decrypt_command_code(message, state):
    code = message.text
    if not db.message_exists(code):
        await message.answer('Такого сообщения не существует\nПопробуйте ещё раз: /decrypt')
        await state.reset_state()
    else:
        await state.update_data(code=code)
        await message.answer('Теперь введите шифр')
        await DecryptForm.waiting_key.set()


@bot.message_handler(state=DecryptForm.waiting_key)
async def decrypt_command_key(message, state):
    key = message.text
    data = await state.get_data()
    msg_encrypted = db.get_message(data['code']).message
    msg = vernam.decrypt(msg_encrypted, key)

    await message.answer('Расшифрованное сообщение:')
    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            await message.answer(msg[x:x+4096])
    else:
        await message.answer(msg)
    
    await DecryptForm.completed.set()


@bot.message_handler()
async def unknown(message):
    await message.answer(UNKNOWN_MSG)


if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=True)
