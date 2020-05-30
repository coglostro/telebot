from glob import glob
import logging
import os
from random import choice


from emoji import emojize
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, error, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.ext import messagequeue as mq

from bot import subscribers
from db import db, get_or_create_user, get_user_emo, toggle_subscription, get_subscribers
from utils import get_keyboard, is_cat


def greet_user(update, context):
    #print(update.message.chat_id)
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(user)
    context.user_data['emo'] = emo
    user_text = f'Привет {emo}'
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_text, reply_markup=get_keyboard())


def talk_to_me(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    emo = get_user_emo(user)
    user_text = f'Привет {user["first_name"]} {emo} Ты написал: {update.message.text}'
    logging.info("User: %s, Chat id: %s, Message: %s", user['username'], update.message.chat.id, update.message.text)
    update.message.reply_text(user_text, reply_markup=get_keyboard())
    #context.bot.send_message(chat_id=update.effective_chat.id, text=user_text)


def send_cat_picture(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    cat_list = glob('images/cat*.jp*g')
    cat_pic = choice(cat_list)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(cat_pic, 'rb'), reply_markup=get_keyboard())

def chenge_avatar(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    
    if 'emo' in user:
        del user['emo']
    emo = get_user_emo(user)
    update.message.reply_text(f'Готово {emo}', reply_markup=get_keyboard())
    #context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def get_contact(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.contact)
    update.message.reply_text(f'Готово {get_user_emo(user)}', reply_markup=get_keyboard())
    #context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def get_location(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    print(update.message.location)
    update.message.reply_text(f'Готово {get_user_emo(user)}', reply_markup=get_keyboard())
    #context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def check_user_photo(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
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

def anketa_start(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Как вас зовут? Напишите имя и Фамилию', reply_markup=ReplyKeyboardRemove())
    return "name"

def anketa_get_name(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_name = update.message.text
    if len(user_name.split(" ")) != 2:
        #update.message.reply_text("Ты пиздишь")
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Введите имя и фамилию')
        return "name"
    else:
        context.user_data['anketa_name'] = user_name
        reply_keyboard = [["1", "2", "3", "4", "5"]]
        update.message.reply_text("Зацени бота от 1 до 5",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        #context.bot.send_message(chat_id=update.effective_chat.id, text=f'Зацени бота от 1 до 5', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return "rating"

def anketa_rating(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    context.user_data['anketa_rating'] = update.message.text
    update.message.reply_text("""Пожалуйста напишите отзыв в свободной форме 
или /cancel чтобы пропустить этот шаг""")
    return "comment"

def anketa_comment(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    context.user_data["anketa_comment"] = update.message.text
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка</b> {anketa_rating}
<b>Комментарий</b> {anketa_comment}""".format(**context.user_data)

    update.message.reply_text(user_text, reply_markup=get_keyboard(),
                                parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def anketa_skip_comment(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    user_text = """
<b>Имя Фамилия:</b> {anketa_name}
<b>Оценка</b> {anketa_rating}""".format(**context.user_data)

    update.message.reply_text(user_text, reply_markup=get_keyboard(),
                                parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def dontknow(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    update.message.reply_text("Не понимаю")

def subscribe (update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    #subscribers.add(update.message.chat_id)
    update.message.reply_text('Вы подписались')

def show_inline(update, context):
    inlinekbd = [[InlineKeyboardButton('Смешно', callback_data='1'),
                    InlineKeyboardButton('Не смешно', callback_data='0')]]
    
    kbd_markup = InlineKeyboardMarkup(inlinekbd)
    update.message.reply_text('Заходят в бар бесконечное количество математиков', reply_markup=kbd_markup)
    
def inline_button_pressed(update, context):
    query = update.callback_query
    try:
        user_choice = int(query.data)
        text = ":-)" if user_choice > 0 else ":-("
    except TypeError:
        text = 'что то пощло не так'
    context.bot.edit_message_text(text=text, chat_id=query.message.chat.id, message_id=query.message.message_id)
    
# Для ветки master
#
# def inline_button_pressed(update, context):
#     query = update.callback_query
#     if query.data in ['cat_good', 'cat_bad']:
#         text = "Круто!" if query.data == 'cat_good' else "Печаль"
    
#         context.bot.edit_message_caption(caption=text, chat_id=query.message.chat.id, message_id=query.message.message_id)

#@mq.queuedmessage
def send_updates(context):
    for user in get_subscribers(db):
        try:
            context.bot.sendMessage(chat_id=user['chat_id'], text="Buzzi")
        except error.BadRequest:
            print('Kasachok')


def unsubscribe (update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text('Вы отписались')
    else:
        update.message.reply_text("Вы не подписаны, нажмите /subscribe чтобы подписаться")

def set_alarm(update, context):
    chat_id = update.message.chat_id

    try:
        #seconds = abs(int(context.args[0]))
        due = int(context.args[0])
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()

        new_job = context.job_queue.run_once(alarm, due, context=chat_id)
        context.chat_data['job'] = new_job
        
        update.message.reply_text("Таймер устонговлен")

    except(IndexError, ValueError):
        update.message.reply_text("Введите количество секунд после /alarm")

#@mq.queuedmessage
def alarm(context):
    job = context.job
    context.bot.send_message(job.context, text="Сроботал будильник")