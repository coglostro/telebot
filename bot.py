import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler,\
     Filters, CallbackQueryHandler
from telegram.ext import messagequeue as mq

from handlers import *
import settings


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

subscribers = set()

# def my_test(context):
#     context.bot.sendMessage(chat_id=567812001, text="Spamonot")
#     context.job.interval +=5
#     if context.job.interval > 10:
#         context.bot.sendMessage(chat_id=567812001, text="chau")
#         context.job.schedule_removal()

def main():

    mybot = Updater(settings.API_KEY, use_context=True)
    
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default = True
    
    logging.info('Бот запускается')

    dp = mybot.dispatcher

    #mybot.job_queue.run_repeating(my_test, interval=5)
    mybot.job_queue.run_repeating(send_updates, interval=5)

    anketa = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Заполнить анкету)$'), anketa_start, pass_user_data=True)],
        states={
            "name": [MessageHandler(Filters.text, anketa_get_name, pass_user_data=True)],
            "rating": [MessageHandler(Filters.regex('^(1|2|3|4|5)$'), anketa_rating, pass_user_data=True)],
            "comment": [MessageHandler(Filters.text, anketa_comment, pass_user_data=True),
                        CommandHandler('skip', anketa_skip_comment, pass_user_data=True)],
        },
        fallbacks=[MessageHandler(
            Filters.text | Filters.video | Filters.photo | Filters.document,
            dontknow,
            pass_user_data=True
        )]
    )
    
    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))
    dp.add_handler(anketa)
    dp.add_handler(CommandHandler('cat', send_cat_picture, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^(Прислать котика)$'), send_cat_picture, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^(Сменить аватар)$'), chenge_avatar, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^(Показать inline-клавиатуру)$'), show_inline, pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(inline_button_pressed))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(CommandHandler('subscribe', subscribe, pass_user_data=True))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe, pass_user_data=True))
    dp.add_handler(CommandHandler('alarm', set_alarm, pass_args=True, pass_job_queue=True, pass_user_data=True))

    dp.add_handler(MessageHandler(Filters.photo, check_user_photo, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=True))

    mybot.start_polling() # ходи в телегу слушай сообщения
    mybot.idle() # Работай пока не остоновят принудительно

if __name__ == "__main__":
    main()