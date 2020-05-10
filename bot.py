from emoji import emojize
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from glob import glob
from random import choice
import logging
import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


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

def get_user_emo(user_data):
    if 'emo' in user_data:
        return user_data['emo']
    else:
        return emojize(choice(settings.USER_EMOJI), use_aliases=True)


def get_contact(update, context):
    emo = get_user_emo(context.user_data)
    print(update.message.contact)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def get_location(update, context):
    emo = get_user_emo(context.user_data)
    print(update.message.location)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Готово {emo}')

def get_keyboard():
    contact_button = KeyboardButton('Контактные данные', request_contact=True)
    location_button = KeyboardButton('Геолокация', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([
                                        ['Прислать котика', 'Сменить аватар'],
                                        [contact_button, location_button]
                                        ],
                                         True)

def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    logging.info('Бот запускается')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))
    dp.add_handler(CommandHandler('cat', send_cat_picture, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^(Прислать котика)$'), send_cat_picture, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^(Сменить аватар)$'), chenge_avatar, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=True))

    mybot.start_polling() # ходи в телегу слушай сообщения
    mybot.idle # Работай пока не остоновят принудительно

if __name__ == "__main__":
    main()