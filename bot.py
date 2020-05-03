from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


def greet_user(update, bot):
    text = 'start'
    print(text)
    bot.bot.send_message(chat_id=update.effective_chat.id, text=text)

def talk_to_me(update, bot):

    user_text = f'Привет {update.message.chat.first_name} Ты написал: {update.message.text}'
    print(user_text)
    logging.info("Привет %s, Chat id: %s, Message: %s", update.message.chat.first_name, update.message.chat.id, update.message.text)
    bot.bot.send_message(chat_id=update.effective_chat.id, text=user_text)


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    logging.info('Бот запускается')

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))


    mybot.start_polling() # ходи в телегу слушай сообщения
    mybot.idle # Работай пока не остоновят принудительно

main()