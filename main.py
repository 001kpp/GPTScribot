import random

import config
import constants
from config import *
from messages import *
from work_generator import CourseWorkFactory, CourseWork, WorkType
import telebot
from telebot import types
from utils import *

bot = telebot.TeleBot(TOKEN)
users_works_count = {}  # user's id: count of works
current_works = []  # users' requests in (chat_id: int, message_id: int, text: str) type
decorating = {}  # link between moderator and work. moderator_id: chat_id: int
factory = CourseWorkFactory(bot=bot)
cw_by_id = {}  # users' works in (chat_id: int, cw: CourseWork) type


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in users_works_count:
        users_works_count[message.from_user.id] = 0
        bot.send_message(ADMIN, f"User @{message.from_user.username} started a bot.")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='📝Сгенерировать работу', callback_data='generate')
    btn2 = types.InlineKeyboardButton(text='❓Узнать о Scribo', callback_data='info')
    btn4 = types.InlineKeyboardButton(text='🤗Чат юзеров', url=CHAT_URL)
    btn5 = types.InlineKeyboardButton(text='📚Отзывы о боте', url=constants.FEEDBACK_URL)
    btn6 = types.InlineKeyboardButton(text='🆘Поддержка', url=constants.SOS_URL)
    markup.add(btn1)
    markup.add(btn2, btn4)
    markup.add(btn5, btn6)
    if message.from_user.id in MODERATORS:
        btn5 = types.InlineKeyboardButton(text='Список доступных работ', callback_data='list')
        markup.add(btn5)
    bot.send_message(message.from_user.id, START_MESSAGE, reply_markup=markup, parse_mode='html')


@bot.message_handler(commands=['menu', 'help', 'cancel'])
def menu(message):
    if message.from_user.id not in users_works_count:
        users_works_count[message.from_user.id] = 0
        bot.send_message(ADMIN, f"User @{message.from_user.username} started a bot.")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='📝Сгенерировать работу', callback_data='generate')
    btn2 = types.InlineKeyboardButton(text='❓Узнать о Scribo', callback_data='info')
    btn4 = types.InlineKeyboardButton(text='🤗Чат юзеров', url=CHAT_URL)
    btn5 = types.InlineKeyboardButton(text='📚Отзывы о боте', url=constants.FEEDBACK_URL)
    btn6 = types.InlineKeyboardButton(text='🆘Поддержка', url=constants.SOS_URL)
    markup.add(btn1)
    markup.add(btn2, btn4)
    markup.add(btn5, btn6)
    if message.from_user.id in MODERATORS:
        btn5 = types.InlineKeyboardButton(text='Список доступных работ', callback_data='list')
        markup.add(btn5)
    bot.send_message(message.from_user.id, MENU_MESSAGE, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split(':')
    markup = types.InlineKeyboardMarkup()
    if req[0] == 'info':
        btn1 = types.InlineKeyboardButton(text='📢Канал проекта', url='https://t.me/scribo_project')
        btn2 = types.InlineKeyboardButton(
            text='📝Отзывы о боте',
            url='https://docs.google.com/spreadsheets/d/1lnW0Rm5TsFEAM__c05odcggWyXn38gFtD1lvw8pQTBw/edit?usp=sharing'
        )
        btn3 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
        markup.add(btn1, btn2)
        markup.add(btn3)
        bot.edit_message_text(
            ABOUT_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            disable_web_page_preview=True
        )
        log(f"User {call.message.chat.id} @{call.message.chat.username} pressed info button", bot)
    elif req[0] == 'generate':
        bot.edit_message_text(
            GENERATE_MESSAGE.format(random.choice(constants.SAMPLE_WORKS)),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='html',
        )
        log(f"User {call.message.chat.id} @{call.message.chat.username} pressed generate button", bot)
    elif req[0] == 'menu':
        btn1 = types.InlineKeyboardButton(text='📝Сгенерировать работу', callback_data='generate')
        btn2 = types.InlineKeyboardButton(text='❓Узнать о Scribo', callback_data='info')
        btn4 = types.InlineKeyboardButton(text='🤗Чат юзеров', url=CHAT_URL)
        btn5 = types.InlineKeyboardButton(text='📚Отзывы о боте', url=constants.FEEDBACK_URL)
        btn6 = types.InlineKeyboardButton(text='🆘Поддержка', url=constants.SOS_URL)
        markup.add(btn1)
        markup.add(btn2, btn4)
        markup.add(btn5, btn6)
        if call.message.chat.id in MODERATORS:
            btn5 = types.InlineKeyboardButton(text='Список доступных работ', callback_data='list')
            markup.add(btn5)
        bot.edit_message_text(
            MENU_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='html',
        )
        log(f"User {call.message.chat.id} @{call.message.chat.username} pressed menu button", bot)
    elif req[0] == 'work':
        btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
        markup.add(btn1)
        if call.message.chat.id not in decorating:
            bot.edit_message_text(
                WORK_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            chat_id = int(req[1])
            message_id = int(req[2])
            file_unique_id = req[3]
            decorating[call.message.chat.id] = chat_id
            current_works.remove((chat_id, message_id, file_unique_id))
        else:
            bot.edit_message_text(
                WRONG_WORK_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
        log(f"Moderator {call.message.chat.id} @{call.message.chat.username} pressed work button", bot)
    elif req[0] == 'list':
        btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
        markup.add(btn1)
        if len(current_works):
            bot.edit_message_text(
                LIST_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            for work_chat_id, work_message_id, work_text in current_works:
                bot.send_message(call.message.chat.id, f"{work_chat_id}\n{work_text}")
        else:
            bot.edit_message_text(
                EMPTY_LIST_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
        log(f"Moderator {call.message.chat.id} @{call.message.chat.username} pressed work button", bot)
    elif req[0] == 'paid':
        log(f"User {call.message.chat.id} @{call.message.chat.username} pressed paid button", bot)
        btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
        markup.add(btn1)
        bot.edit_message_text(
            WAIT_MESSAGE.format(price=config.PRICE),
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='html'
        )
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            text='✅Да!',
            callback_data=f'really_paid:{call.message.chat.id}:{call.message.message_id}:{call.message.chat.username}',
        )
        btn2 = types.InlineKeyboardButton(
            text='❌Нет(',
            callback_data=f'not_paid:{call.message.chat.id}:{call.message.message_id}:{call.message.chat.username}',
        )
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(
            EMERGENCY_ADMIN,
            PAID_QUESTION_MESSAGE.format(call.message.chat.id, call.message.chat.username),
            reply_markup=markup,
        )
    elif req[0] == "really_paid":
        user_id = int(req[1])
        message_id = int(req[2])
        username = req[3]
        log(
            f"Emergency admin {call.message.chat.id} pressed really paid button for user {user_id} @{username}",
            bot,
        )
        bot.edit_message_text(
            REALLY_PAID_MESSAGE,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
        for i in range(TRIES_COUNT):
            cw: CourseWork = cw_by_id.get(user_id)
            if not cw:
                send_problem(ADMIN, user_id)
                break
            try:
                if cw.save(free=False):
                    bot.delete_message(user_id, message_id)
                    send_work(cw, ADMIN, user_id, free=False)
                    remove_work(cw.name)
                    cw.delete()
                    break
            except Exception as e:
                log(f"Exception while saving: {e}")
            finally:
                cw.delete(i < TRIES_COUNT - 1)
        else:
            bot.send_message(ADMIN, PROBLEM_MESSAGE, reply_markup=markup)
    elif req[0] == "not_paid":
        user_id = int(req[1])
        message_id = int(req[2])
        username = req[3]
        log(f"Emergency admin {call.message.chat.id} pressed not paid button for user {user_id} @{username}", bot)
        bot.edit_message_text(
            NOT_PAID_MESSAGE,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
        log(f"User {user_id} didn't pay!", bot)
        btn1 = types.InlineKeyboardButton(text='✅Я оплатил', callback_data='paid')
        markup.add(btn1)
        btn2 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
        markup.add(btn2)
        bot.edit_message_text(
            WRONG_MESSAGE.format(price=config.PRICE),
            reply_markup=markup,
            chat_id=user_id,
            message_id=message_id,
            parse_mode='html'
        )
    elif req[0] == "size":
        bot.send_message(
            ADMIN,
            BUTTON_PRESSED_MESSAGE.format(call.message.chat.id, call.message.chat.username, req[1]),
        )
        if call.message.chat.id not in cw_by_id.keys():
            bot.send_message(
                ADMIN,
                GENERATE_AGAIN_MESSAGE,
            )
            bot.edit_message_text(
                GENERATE_AGAIN_MESSAGE,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            return
        cw = cw_by_id[call.message.chat.id]
        cw.size = int(req[1])

        btn1 = types.InlineKeyboardButton(text='Курсовая', callback_data="type:coursework")
        btn2 = types.InlineKeyboardButton(text='Дипломная', callback_data="type:diploma")
        btn3 = types.InlineKeyboardButton(text='Реферат', callback_data="type:reference")
        markup.add(btn1, btn2, btn3)
        btn4 = types.InlineKeyboardButton(text='Доклад', callback_data="type:report")
        btn5 = types.InlineKeyboardButton(text='Исследование', callback_data="type:research")
        btn6 = types.InlineKeyboardButton(text='Отчет по практике', callback_data="type:practice")
        markup.add(btn4, btn5, btn6)
        btn7 = types.InlineKeyboardButton(text='🤷‍♂️Любая работа', callback_data="type:reference")
        btn8 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
        markup.add(btn7)
        markup.add(btn8)
        bot.edit_message_text(
            WORK_TYPE_MESSAGE.format(cw.name),
            chat_id=call.message.chat.id,
            parse_mode='html',
            message_id=call.message.message_id,
            reply_markup=markup,
        )
    elif req[0] == "type":
        bot.send_message(
            ADMIN,
            BUTTON_PRESSED_MESSAGE.format(call.message.chat.id, call.message.chat.username, req[1]),
        )
        if call.message.chat.id not in cw_by_id.keys():
            bot.send_message(
                ADMIN,
                GENERATE_AGAIN_MESSAGE,
            )
            bot.edit_message_text(
                GENERATE_AGAIN_MESSAGE,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            return
        cw = cw_by_id[call.message.chat.id]
        cw.work_type = WorkType.from_name(req[1])

        status_message = bot.edit_message_text(
            STATUS_MESSAGE.format(constants.UNREADY_SYMBOL * 10),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup,
        )

        for i in range(TRIES_COUNT):
            bot.send_message(ADMIN, ATTEMPT_MESSAGE.format(i))
            factory.generate_coursework(cw, status_message)
            try:
                if cw.save():
                    send_work(cw, ADMIN, call.message.chat.id)
                    remove_work(cw.name)
                    cw.delete()
                    break
            except Exception as e:
                log(f"Exception while saving: {e}")
            finally:
                cw.delete(i < TRIES_COUNT - 1)
        else:
            bot.send_message(ADMIN, PROBLEM_MESSAGE, reply_markup=markup)


@bot.message_handler(content_types=['document'])
def get_document(message):
    if message.from_user.id in MODERATORS:
        if message.from_user.id in decorating:
            moderator_id = message.from_user.id
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
            markup.add(btn1)
            bot.send_message(moderator_id, GOOD_WORK_MESSAGE, reply_markup=markup)
            bot.copy_message(decorating[moderator_id], moderator_id, message.id)
            bot.send_message(decorating[moderator_id], READY_MESSAGE, reply_markup=markup)
            del decorating[moderator_id]
        else:
            bot.send_message(message.from_user.id, NO_WORKS_MESSAGE, parse_mode='Markdown')
    else:
        bot.send_message(message.from_user.id, IDK_MESSAGE)
        log(f"User {message.from_user.id} sent some document", bot)


def remove_work(work_name):
    for work in current_works:
        if work[2] == work_name:
            current_works.remove(work)
            break


def send_work(cw: CourseWork, moderator: int, user: int, free: bool = True) -> None:
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
    for work_type in constants.WORK_TYPES:
        try:
            bot.send_document(moderator, open(cw.file_name(work_type), 'rb'))
            bot.send_document(user, open(cw.file_name(work_type), 'rb'))
        except Exception as e:
            log(f"Can't send a document: {e}", bot)
    if free:
        try:
            btn2 = types.InlineKeyboardButton(text='✅Я оплатил', callback_data='paid')
            markup.add(btn1)
            bot.send_message(moderator, FREE_MESSAGE.format(price=config.PRICE), reply_markup=markup, parse_mode='html')
            markup = types.InlineKeyboardMarkup()
            markup.add(btn2)
            markup.add(btn1)
            bot.send_message(user, FREE_MESSAGE.format(price=config.PRICE), reply_markup=markup, parse_mode='html')
        except Exception as e:
            log(f"Can't send a document: {e}", bot)
    else:
        markup.add(btn1)
        bot.send_message(moderator, READY_MESSAGE, reply_markup=markup)
        bot.send_message(user, READY_MESSAGE, reply_markup=markup)


def send_problem(moderator: int, user: int) -> None:
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
    markup.add(btn1)
    bot.send_message(moderator, PAID_PROBLEM_MESSAGE, reply_markup=markup)
    bot.send_message(user, PAID_PROBLEM_MESSAGE, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_message(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
    markup.add(btn1)
    if message.from_user.id in MODERATORS and message.text.lower() == "беру":
        if message.from_user.id in decorating:
            bot.send_message(message.from_user.id, WRONG_WORK_MESSAGE, reply_markup=markup)
        elif message.reply_to_message:
            bot.send_message(message.from_user.id, WORK_MESSAGE, reply_markup=markup)
            reply_chat_id = int(message.reply_to_message.text.split("\n")[0])
            decorating[message.from_user.id] = reply_chat_id
            remove_work(message.reply_to_message.text.partition("\n")[2])
        else:
            bot.send_message(message.from_user.id, WRONG_REPLY_MESSAGE, reply_markup=markup)
        log(f"Moderator {message.from_user.id} sent беру", bot)
    if message.from_user.id in MODERATORS and message.text.lower() == "сгенерировать":
        log(f"Moderator {message.from_user.id} sent сгенерировать", bot)
        if message.reply_to_message:
            reply_chat_id = int(message.reply_to_message.text.split("\n")[0])
            markup = types.InlineKeyboardMarkup()
            markup.add(btn1)
            status_message = bot.send_message(
                reply_chat_id,
                STATUS_MESSAGE.format(constants.UNREADY_SYMBOL * 10),
                parse_mode='Markdown',
                reply_markup=markup,
            )
            for i in range(TRIES_COUNT):
                bot.send_message(message.from_user.id, ATTEMPT_MESSAGE.format(i), reply_markup=markup)
                cw = factory.create_coursework(message.reply_to_message.text.split("\n")[1])
                cw_by_id[reply_chat_id] = cw
                factory.generate_coursework(cw, status_message)
                try:
                    if cw.save():
                        send_work(cw, message.from_user.id, reply_chat_id)
                        remove_work(cw.name)
                        cw.delete()
                        break
                except Exception as e:
                    log(f"Exception while saving: {e}")
                finally:
                    cw.delete(i < TRIES_COUNT - 1)
            else:
                bot.send_message(message.from_user.id,
                                 PROBLEM_MESSAGE.format(message.reply_to_message.text.split("\n")[1]),
                                 reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, WRONG_REPLY_MESSAGE, reply_markup=markup)
    elif message.from_user.id not in MODERATORS:
        for moderator_id in MODERATORS:
            try:
                bot.send_message(moderator_id, f"{message.from_user.id}\n{message.text}")
            except telebot.apihelper.ApiTelegramException:
                print(f"Moderator {moderator_id} has not started the bot yet")
        bot.send_message(
            ADMIN,
            SENT_WORK_MESSAGE.format(message.from_user.id, message.from_user.username, message.text),
        )
        current_works.append((message.from_user.id, message.id, message.text))
        cw = factory.create_coursework(message.text)
        cw_by_id[message.from_user.id] = cw
        markup = types.InlineKeyboardMarkup()
        btn10 = types.InlineKeyboardButton(text='5-10', callback_data="size:10")
        btn20 = types.InlineKeyboardButton(text='10-20', callback_data="size:20")
        btn30 = types.InlineKeyboardButton(text='20-30', callback_data="size:30")
        markup.add(btn10, btn20, btn30)
        btn40 = types.InlineKeyboardButton(text='30-40', callback_data="size:40")
        btn50 = types.InlineKeyboardButton(text='40-50', callback_data="size:50")
        btn60 = types.InlineKeyboardButton(text='50-60', callback_data="size:60")
        markup.add(btn40, btn50, btn60)
        btn2 = types.InlineKeyboardButton(text='🤷‍♂️Любой размер работы', callback_data="size:20")
        markup.add(btn2)
        markup.add(btn1)
        bot.send_message(
            message.from_user.id,
            WORK_SIZE_MESSAGE.format(message.text),
            parse_mode='html',
            reply_markup=markup,
        )


log("Bot is running!", bot)
bot.infinity_polling()
