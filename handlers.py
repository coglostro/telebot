from utils import get_user_emo, get_keyboard, is_cat
from glob import glob
import os
from random import choice
import logging

def greet_user(update, context):
    emo = get_user_emo(context.user_data)
    context.user_data['emo'] = emo
    user_text = f'Привет {emo}'
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_text, reply_markup=my_keyboard)


def talk_to_me(update, context):
    emo = get_user_emo(context.user_data)
    user_text = f'Привет {update.message.chat.first_name} {emo} Ты написал: {update.message.text}'
    logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.first_name, update.message.chat.id, update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_text)


def send_cat_picture(update, context):
    cat_list = glob('images/cat*.jp*g')
    cat_pic = choice(cat_list)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(cat_pic, 'rb'))

def chenge_avatar(update, context):
    if 'emo' in context.user_data:
        del context.user_data['emo']
    emo = get_user_emo(context.user_data)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def get_contact(update, context):
    emo = get_user_emo(context.user_data)
    print(update.message.contact)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def get_location(update, context):
    emo = get_user_emo(context.user_data)
    print(update.message.location)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def check_user_photo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Обрабатываю фото')
    os.makedirs('downloads', exist_ok=True)
    photo_file = context.bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', f'{photo_file.file_id}.jpg')
    photo_file.download(filename)
    #context.bot.send_message(chat_id=update.effective_chat.id, text=f'Файл сохранен')
    if is_cat(filename):
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Обнаружен котик, добавляю в библиотеку.')
        new_filename = os.path.join('images', f'cat_{photo_file.file_id}.jpg')
        os.rename(filename, new_filename)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'неОбнаружен котик.')
        os.remove(filename)