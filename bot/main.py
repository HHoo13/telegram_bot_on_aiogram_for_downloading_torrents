import os
import pathlib
from zipfile import ZipFile, ZIP_DEFLATED

from PyBitTorrent import TorrentClient, TorrentFile
from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType, InputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
# инициализируем базу данных
from connection import DataBase
from logic import create_dirs, catalog1, data, del_dir

db = DataBase()

# инициализируем бота
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    print('Бот вышел в онлайн')


# класс машины состояний
class Chatting(StatesGroup):
    msg = State()


# файд языка

lang = None


# magnit = r"C:\Users\Shirinov\PycharmProjects\torrent_bot\catalog\magnits"
# torrents = r"C:\Users\Shirinov\PycharmProjects\torrent_bot\catalog\torrents"
# archives = r'C:\Users\Shirinov\PycharmProjects\torrent_bot\catalog\archives'

# хендлер команды /start
@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    global lang
    button_settings = KeyboardButton(lang['settings'])
    mark_menu = ReplyKeyboardMarkup(resize_keyboard=True)
    mark_menu.add(button_settings)
    try:
        await state.finish()
        db.get_user(message.from_user.id)
        if not db.i:
            db.add_user_into_bd(message.from_user.id)
            await message.answer(lang['hello'],
                                 reply_markup=mark_menu)
        db.get_lang(message.from_user.id)
        lang = data[f'{db.lang[0]}']
        await Chatting.next()
        await chatting(message, state)
    except Exception as e:
        print(e)


# @dp.message_handler(content_types=lang['settings'])
@dp.message_handler(commands=['settings'], state='*')
async def settings(message: types.Message, state: FSMContext):
    ru = KeyboardButton(data['ru']['flag'])
    en = KeyboardButton(data['en']['flag'])
    menu_msg = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_msg.add(ru, en)
    await message.answer(lang['choose'], reply_markup=menu_msg)
    await Chatting.next()
    # await chatting(message, state)


@dp.message_handler(content_types=ContentType.TEXT)
@dp.message_handler(state=Chatting.msg)
async def chatting(message: types.message, state: FSMContext):
    global lang
    #  Функция где и происходить общения и обмен ТЕКСТОВЫМИ сообщениями
    try:
        await state.update_data(msg=message.text)
        user_data = await state.get_data()
        if user_data['msg'] == lang['settings']:
            await settings(message, state)
        elif user_data['msg'] == lang['send']:
            await message.answer(lang['done'], reply_markup=types.ReplyKeyboardRemove())
            await get(message, state)
        elif user_data['msg'] == data['ru']['flag']:
            db.set_lang(telegram_id=message.from_user.id, lang='ru')
            db.get_lang(message.from_user.id)
            lang = data[f'{db.lang[0]}']
            await message.answer(lang['done'], reply_markup=types.ReplyKeyboardRemove())
        elif user_data['msg'] == data['en']['flag']:
            db.set_lang(telegram_id=message.from_user.id, lang='en')
            db.get_lang(message.from_user.id)
            lang = data[f'{db.lang[0]}']
            await message.answer(lang['done'], reply_markup=types.ReplyKeyboardRemove())
            # await mag(message, state)
    except Exception as e:
        print(e)
        await state.finish()


@dp.message_handler(state='*')
async def get(message: types.Message, state: FSMContext):
    await message.answer(lang["sending"])
    create_dirs('archive', f'{message.from_user.id}')
    with ZipFile(f"{message.from_user.id}.zip", "w", ZIP_DEFLATED, compresslevel=9) as archive:
        directory = pathlib.Path(f'{catalog1}\\{message.from_user.id}\\archive')
        #  дирктория которую хотим заархивировать
        for file_path in directory.rglob("*"):
            archive.write(file_path, arcname=file_path.relative_to(directory))
        del_dir(first=f'{catalog1}\\{message.from_user.id}\\torrent',
                second=f'{catalog1}\\{message.from_user.id}\\magnet')
    await message.answer_document(InputFile(f'{catalog1}\\{message.from_user.id}\\archive\\{message.from_user.id}.zip'))
    await state.finish()

@dp.message_handler(state='*')
async def mag(message: types.Message, state: FSMContext):
    button = KeyboardButton(lang['send'])
    mark_menu = ReplyKeyboardMarkup(resize_keyboard=True)
    mark_menu.add(button)
    await message.answer(lang["downloaded"], reply_markup=mark_menu)
    await state.finish()


@dp.message_handler(content_types=['document'], state='*')
async def torrent(message, state: FSMContext):
    try:
        create_dirs('magnet', f'{message.from_user.id}')
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        name = message.document.file_name
        if '.torrent' not in name:
            await message.delete()
            await message.answer(lang["error_magnet"])
        else:
            await message.answer(lang["download"])
            await bot.download_file(file_path, name)
            create_dirs('torrent', f'{message.from_user.id}')
            await message.answer(lang["downloading"])
            a = TorrentFile(torrent=f'{catalog1}\\{message.from_user.id}\\magnet\\{name}')
            n = a.file_name
            if f'{n}' not in os.listdir(f'{catalog1}\\{message.from_user.id}\\torrent'):
                try:
                    client = TorrentClient(torrent=f'{catalog1}\\{message.from_user.id}\\magnet\\{name}', output_dir=os.getcwd())
                    client.start()
                except Exception as e:
                    print(e)
            await state.finish()
            await mag(message, state)
    except Exception as e:
        await state.finish()
        print(e)



@dp.message_handler()
async def end(message: types.Message):
    #  Функция непредсказумогого ответа
    await message.answer('/start /settings')


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
