from __future__ import print_function
from emoji import emojize
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, \
     RegexHandler
from datetime import timedelta, datetime
from telegram.ext import messagequeue as mq

import logging
import mysql.connector
import telegramcalendar

PROXY = {'proxy_url': 'socks5://t1.learn.python.ru:1080',
         'urllib3_proxy_kwargs': {'username': 'learn', 'password': 'python'}}

TOKEN = "728852231:AAEZLnITK0BYNpAfQ4DCIC8CjpyiYLYUpIo"

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

logger = logging.getLogger(__name__)

FIRST, SECOND, THIRD, FOURTH, FIVE = range(5)

conn = mysql.connector.connect(host='mysql.j949396.myjino.ru',
                               database='j949396_blondi-service',
                               user='j949396',
                               password='qwerty')
cursor = conn.cursor()

smiles = [emojize(':heavy_plus_sign:', use_aliases=True),
          emojize(':ledger:', use_aliases=True),
          emojize(':information_source:', use_aliases=True),
          emojize(':x:', use_aliases=True),
          emojize(':calendar:', use_aliases=True),
          emojize(':man:', use_aliases=True),
          emojize(':scissors:', use_aliases=True),
          emojize(':clock230:', use_aliases=True),
          emojize(':white_check_mark:', use_aliases=True),
          emojize(':no_entry_sign:', use_aliases=True),
          emojize(':leftwards_arrow_with_hook:', use_aliases=True),
          emojize(':telephone_receiver:', use_aliases=True),
          emojize(':star:', use_aliases=True),
          emojize(':nail_care:', use_aliases=True)]

start_keyboard = ReplyKeyboardMarkup([['Добавить запись {}'.format(smiles[0])],
                                      ['Мои записи {}'.format(smiles[1]),
                                       'О нас {}'.format(smiles[2])]],
                                     resize_keyboard=True,
                                     one_time_keyboard=True)
menu_keyboard = ReplyKeyboardMarkup([['Вернуться в главное меню {}'.format(smiles[10])]],
                                    resize_keyboard=True)


def talk_to_me(bot, update):
    # функция - ответ на текст введенный пользователем
    update.message.reply_text('Нажмите /start для запуска бота')


def greet_user(bot, update, user_data):
    """ /start """
    text = 'Вас приветствует salon_service_bot!'
    update.message.reply_text(text, reply_markup=start_keyboard)


def choose_room(bot, update, user_data):
    """ Ограничение количества записей """
    if user_data == {}:
        pass
    else:
        if len(max_entries) < 3:
            pass
        else:
            return update.message.reply_text('У Вас максимально возможное количество записей!',
                                             reply_markup=ReplyKeyboardMarkup([['Мои записи {}'.format(smiles[1])]],
                                                                              resize_keyboard=True,
                                                                              one_time_keyboard=True))
    update.message.reply_text('Выберите зал:',
                              reply_markup=ReplyKeyboardMarkup([['Маникюрный зал {}'.format(smiles[13]),
                                                                 'Парикмахерский зал {}'.format(smiles[6])]],
                                                               resize_keyboard=True,
                                                               one_time_keyboard=True))


def choose_service(bot, update, user_data):
    """ Вызов инлайн клавиатуры с услугами """

    sql = "SELECT service, price FROM barbershop_room"
    cursor.execute(sql)
    data_base = cursor.fetchall()

    sql_2 = "SELECT service, price FROM manicure_room"
    cursor.execute(sql_2)
    data_base_2 = cursor.fetchall()

    global all_services
    all_price = [price[1] for price in data_base]
    all_services = [service[0] for service in data_base]

    global all_services_2
    all_price_2 = [price_2[1] for price_2 in data_base_2]
    all_services_2 = [services_2[0] for services_2 in data_base_2]

    user_text = update.message.text
    if user_text == 'Парикмахерский зал {}'.format(smiles[6]):
        info_text = '{} \n {} - {} \n {} - {} \n {} - {} \n {} - {} \n'.format('Выберите услугу:',
                                                                               all_services[0], all_price[0],
                                                                               all_services[1], all_price[1],
                                                                               all_services[2], all_price[2],
                                                                               all_services[3], all_price[3])
        row = [InlineKeyboardButton(i, callback_data=str(i)) for i in all_services[0:2]]
        keyboard = [row]
        row = [InlineKeyboardButton(i, callback_data=str(i)) for i in all_services[2:4]]
        keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(info_text, reply_markup=reply_markup)
    elif user_text == 'Маникюрный зал {}'.format(smiles[13]):
        info_text_2 = '{} \n {} - {} \n {} - {} \n'.format('Выберите услугу:',
                                                           all_services_2[0], all_price_2[0],
                                                           all_services_2[1], all_price_2[1])
        row = [InlineKeyboardButton(i, callback_data=str(i)) for i in all_services_2[0:2]]
        keyboard = [row]
        row = [InlineKeyboardButton(i, callback_data=str(i)) for i in all_services_2[2:4]]
        keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(info_text_2, reply_markup=reply_markup)
    return FIRST


def choose_master(bot, update, user_data):
    """ Вызов инлайн клавиатуры с мастерами """

    query = update.callback_query
    service = query.data

    sql = "SELECT * FROM barbershop_masters"
    cursor.execute(sql)
    data_base = cursor.fetchall()

    sql_2 = "SELECT * FROM manicure_masters"
    cursor.execute(sql_2)
    data_base_2 = cursor.fetchall()

    all_info = [i for i in data_base]
    all_info_2 = [i for i in data_base_2]

    if service in all_services:
        for i in all_info:
            row = [InlineKeyboardButton(i[0], callback_data=str(i[0]))]
            list_1 = [row]
            reply_markup = InlineKeyboardMarkup(list_1)
            bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=i[1],
                           caption='*Мастер:* {} \n'
                                   '*Опыт работы:* {} \n'
                                   '*Рейтинг:* {}'.format(i[0], i[2], smiles[12]),
                           parse_mode="Markdown",
                           reply_markup=reply_markup)
    elif service in all_services_2:
        for i in all_info_2:
            row = [InlineKeyboardButton(i[0], callback_data=str(i[0]))]
            list_1 = [row]
            reply_markup = InlineKeyboardMarkup(list_1)
            bot.send_photo(chat_id=update.callback_query.from_user.id,
                           photo=i[1],
                           caption='*Мастер:* {} \n'
                                   '*Опыт работы:* {} \n'
                                   '*Рейтинг:* {}'.format(i[0], i[2], smiles[12]),
                           parse_mode="Markdown",
                           reply_markup=reply_markup)
    bot.delete_message(chat_id=update.callback_query.from_user.id,
                       message_id=query.message.message_id)
    user_data['service'] = query.data
    return SECOND


def calendar(bot, update, user_data):
    """ Вызов инлайн клавиатуры с календарем """

    query = update.callback_query
    name = query.data
    if name == 'Вова':
        bot.delete_message(chat_id=query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(text='Выберите дату: {}'.format(smiles[4]),
                         chat_id=query.from_user.id,
                         message_id=query.message.message_id,
                         reply_markup=telegramcalendar.create_calendar_vova())
    elif name == 'Дима':
        bot.delete_message(chat_id=query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(text='Выберите дату: {}'.format(smiles[4]),
                         chat_id=query.from_user.id,
                         message_id=query.message.message_id,
                         reply_markup=telegramcalendar.create_calendar_dima())
    elif name == 'Сергей':
        bot.delete_message(chat_id=query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(text='Выберите дату: {}'.format(smiles[4]),
                         chat_id=query.from_user.id,
                         message_id=query.message.message_id,
                         reply_markup=telegramcalendar.create_calendar_serg())
    else:
        bot.delete_message(chat_id=query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(text='Выберите дату: {}'.format(smiles[4]),
                         chat_id=query.from_user.id,
                         message_id=query.message.message_id,
                         reply_markup=telegramcalendar.create_calendar())
    user_data['name'] = query.data
    return THIRD


def time_check(bot, update, user_data):
    """ Вывод инлайн клавиатуры со временем """

    query = update.callback_query
    if user_data['name'] == 'Вова':
        selected, date = telegramcalendar.process_calendar_selection_vova(bot, update)
    elif user_data['name'] == 'Дима':
        selected, date = telegramcalendar.process_calendar_selection_dima(bot, update)
    elif user_data['name'] == 'Сергей':
        selected, date = telegramcalendar.process_calendar_selection_serg(bot, update)
    else:
        selected, date = telegramcalendar.process_calendar_selection(bot, update)

    sql = "SELECT * FROM time_to_barbers"
    cursor.execute(sql)
    data_base = cursor.fetchall()

    sql_2 = "SELECT * FROM record_info"
    cursor.execute(sql_2)
    data_base_2 = cursor.fetchall()

    if selected:
        all_time = [i[0] for i in data_base if user_data.get('name') in i[1]]
        for z in data_base_2:
            if user_data.get('name') in z[1] and date.strftime("%Y-%m-%d") in z[2] and z[3] in all_time:
                all_time.remove(z[3])
                if len(all_time) < 6:
                    all_time.append('Нет записи')
        keyboard = []
        row = [InlineKeyboardButton(i, callback_data=str(i)) for i in all_time[0:3]]
        keyboard.append(row)
        row = [InlineKeyboardButton(i, callback_data=str(i)) for i in all_time[3:6]]
        keyboard.append(row)
        row = [InlineKeyboardButton('Выбрать другой день', callback_data='Выбрать другой день')]
        keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text='Выберите время: {}'.format(smiles[6]),
                              chat_id=update.callback_query.from_user.id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
    user_data['date'] = date.strftime("%Y-%m-%d")
    return FOURTH


def contact(bot, update, user_data):
    """ Запрос контактов """

    query = update.callback_query
    if query.data == "Нет записи":
        bot.answer_callback_query(callback_query_id=query.id)
    elif query.data == 'Выбрать другой день' and user_data['name'] == 'Вова':
        bot.edit_message_text(text='Выберите дату: {} '.format(smiles[4]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=telegramcalendar.create_calendar_vova())
        return THIRD
    elif query.data == 'Выбрать другой день' and user_data['name'] == 'Дима':
        bot.edit_message_text(text='Выберите дату: {} '.format(smiles[4]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=telegramcalendar.create_calendar_dima())
        return THIRD
    elif query.data == 'Выбрать другой день' and user_data['name'] == 'Сергей':
        bot.edit_message_text(text='Выберите дату: {} '.format(smiles[4]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=telegramcalendar.create_calendar_serg())
        return THIRD
    elif query.data == 'Выбрать другой день':
        bot.edit_message_text(text='Выберите дату: {} '.format(smiles[4]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=telegramcalendar.create_calendar())
        return THIRD
    else:
        contact_button = KeyboardButton('Контактные данные {}'.format(smiles[11]), request_contact=True)
        my_keyboard = ReplyKeyboardMarkup([[contact_button]],
                                          resize_keyboard=True,
                                          one_time_keyboard=True)
        bot.send_message(chat_id=update.callback_query.from_user.id,
                         text="Отправьте Ваши контактные данные для уточнения заказа:",
                         reply_markup=my_keyboard)
        bot.delete_message(chat_id=update.callback_query.from_user.id,
                           message_id=query.message.message_id)
        user_data['time'] = query.data


def get_contact(bot, update, user_data, job_queue):
    """ Запись выбора пользователя в БД, создание переменных для напоминаний """

    print(update.message.contact)
    user_data['number'] = update.message.contact.phone_number
    user_data['first_name'] = update.message.contact.first_name

    """ Запись всех данных в БД """

    user_dict = [i for i in dict.values(user_data)]
    record = tuple(user_dict)

    record_insert = "INSERT INTO record_info (service, name, date, time, number, first_name)" \
                    " VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(record_insert, record)
    conn.commit()

    """ Создание напоминаний """

    sql = "SELECT * FROM record_info"
    cursor.execute(sql)
    data_base = cursor.fetchall()

    """ Словарь для ограничения количества записей """
    global max_entries
    max_entries = []

    """ Словарь для напоминаний """
    global alarm_info
    alarm_info = []

    user_entry = []
    for z in data_base:
        if user_data.get('number') == z[4]:
            alarm_info.extend((z[0:4]))
            user_entry.extend((z[2:4]))
            max_entries.append(z[4])

    alert = timedelta(hours=5, minutes=47)

    if len(user_entry) == 2:
        date_format = datetime.strptime((' '.join(user_entry[0:2])), "%Y-%m-%d %H:%M")
        notify = date_format + alert
        print(notify)
        job_queue.run_once(alarm, when=notify, context=update.message.chat_id, name='job')
    elif len(user_entry) == 4:
        date_format = datetime.strptime((' '.join(user_entry[2:4])), "%Y-%m-%d %H:%M")
        notify_1 = date_format + alert
        print(notify_1)
        job_queue.run_once(alarm_1, when=notify_1, context=update.message.chat_id, name='job')
    elif len(user_entry) == 6:
        date_format = datetime.strptime((' '.join(user_entry[4:6])), "%Y-%m-%d %H:%M")
        notify_2 = date_format + alert
        print(notify_2)
        job_queue.run_once(alarm_2, when=notify_2, context=update.message.chat_id, name='job')

    global job_list
    job_list = [i for i in job_queue.get_jobs_by_name('job')]

    update.message.reply_text("Спасибо! \n"
                              "Вы можете посмотреть информацию о своих записях в главном меню",
                              reply_markup=start_keyboard)


@mq.queuedmessage
def alarm(bot, job):
    bot.send_message(chat_id=job.context, text=('Запись 1 ' + ', '.join(alarm_info[0:4])))
    # 'Напоминаем, что Вы записаны на услугу {} к мастеру {} через 1 час!'.format(info_9[0], info_9[1])


@mq.queuedmessage
def alarm_1(bot, job):
    bot.send_message(chat_id=job.context, text=('Запись 2 ' + ', '.join(alarm_info[4:8])))


@mq.queuedmessage
def alarm_2(bot, job):
    bot.send_message(chat_id=job.context, text=('Запись 3 ' + ', '.join(alarm_info[8:12])))


def my_entry(bot, update, user_data):
    """ Вывод информации о записях """

    sql = "SELECT * FROM record_info"
    cursor.execute(sql)
    data_base = cursor.fetchall()

    sql_1 = "SELECT service, price FROM barbershop_room"
    cursor.execute(sql_1)
    data_base_1 = cursor.fetchall()

    sql_2 = "SELECT service, price FROM manicure_room"
    cursor.execute(sql_2)
    data_base_2 = cursor.fetchall()

    if user_data == {}:
        update.message.reply_text('У вас нет записей {}'.format(smiles[9]),
                                  reply_markup=start_keyboard)
    else:
        global check_price
        check_price = []
        entries = []
        for z in data_base:
            if user_data.get('number') == z[4]:
                entries.extend((z[0:4]))
                i = [i for i in data_base_1]
                q = [i for i in data_base_2]
                for m in i:
                    if z[0] in m[0]:
                        check_price.append(m[1])
                for p in q:
                    if z[0] in p[0]:
                        check_price.append(p[1])

        total_sum = sum(check_price[0:])
        keyboard = []
        if len(entries) == 4:
            row = [InlineKeyboardButton((', '.join(entries[0:4])), callback_data='1')]
            main_menu = [InlineKeyboardButton('Вернуться в главное меню {}'.format(smiles[10]), callback_data='0')]
            keyboard.extend((row, main_menu))
        elif len(entries) == 8:
            row = [InlineKeyboardButton((', '.join(entries[0:4])), callback_data='1')]
            row_1 = [InlineKeyboardButton((', '.join(entries[4:8])), callback_data='2')]
            all_entries = [InlineKeyboardButton('Отменить все записи {}'.format(smiles[3]), callback_data='Отмена')]
            main_menu = [InlineKeyboardButton('Вернуться в главное меню {}'.format(smiles[10]), callback_data='0')]
            keyboard.extend((row, row_1, all_entries, main_menu))
        elif len(entries) > 8:
            row = [InlineKeyboardButton((', '.join(entries[0:4])), callback_data='1')]
            row_1 = [InlineKeyboardButton((', '.join(entries[4:8])), callback_data='2')]
            row_2 = [InlineKeyboardButton((', '.join(entries[8:12])), callback_data='3')]
            all_entries = [InlineKeyboardButton('Отменить все записи {}'.format(smiles[3]), callback_data='Отмена')]
            main_menu = [InlineKeyboardButton('Вернуться в главное меню {}'.format(smiles[10]), callback_data='0')]
            keyboard.extend((row, row_1, row_2, all_entries, main_menu))
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            update.message.reply_text('Клиент: ' + user_data.get('first_name') + '\n'
                                      + '\n'
                                      'Итоговая сумма: ' + str(total_sum) + '\n'
                                      + '\n'
                                      'Ниже представлена краткая информация о ваших записях.' + '\n'
                                      'Чтобы отменить запись -  просто нажмите на нее!',
                                      reply_markup=reply_markup)
        except AttributeError:
            bot.edit_message_text('Клиент: ' + user_data.get('first_name') + '\n'
                                  + '\n'
                                  'Итоговая сумма: ' + str(total_sum) + '\n'
                                  + '\n'
                                  'Ниже представлена краткая информация о ваших записях.' + '\n'
                                  'Чтобы отменить запись -  просто нажмите на нее!',
                                  chat_id=update.callback_query.message.chat_id,
                                  message_id=update.callback_query.message.message_id,
                                  reply_markup=reply_markup)
        return FIVE


def cancel_entries(bot, update, user_data, job_queue):
    """ Удаление записей из базы данных и напоминаний"""

    query = update.callback_query
    service = query.data

    sql = "SELECT * FROM record_info"
    cursor.execute(sql)
    data_base = cursor.fetchall()

    info_list = []
    for data_list in data_base:
        if user_data.get('number') in data_list[4]:
            info_list.extend((data_list[0:4]))

    if service == '1' and len(info_list) == 4:
        info_tuple = tuple(info_list[0:4])
        new_tuple = info_tuple + (user_data.get('number'),)
        cursor.execute("DELETE FROM record_info WHERE"
                       " service = %s and name = %s and date = %s and time = %s and number = %s",
                       new_tuple)
        conn.commit()

        user_data.clear()
        max_entries.clear()

        """ Удаление всех напоминаний """
        job_queue.stop()
        bot.delete_message(chat_id=update.callback_query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(chat_id=update.callback_query.from_user.id,
                         text='У вас нет записей {}'.format(smiles[9]),
                         reply_markup=start_keyboard)
    elif service == '1':
        info_tuple = tuple(info_list[0:4])
        new_tuple = info_tuple + (user_data.get('number'),)
        cursor.execute("DELETE FROM record_info WHERE"
                       " service = %s and name = %s and date = %s and time = %s and number = %s",
                       new_tuple)
        conn.commit()

        max_entries.pop()

        """ Удаление напоминаний """
        if len(job_list) == 2:
            print('убрали первый джоб и джоба было 2')
            job_list[0].schedule_removal()
        if len(info_list) == 12:
            print('убрали первый джоб')
            job_list[0].schedule_removal()
        if len(info_list) == 8 and len(job_list) == 3:
            print('убрали второй джоб')
            job_list[1].schedule_removal()
        bot.edit_message_reply_markup(chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id,
                                      reply_markup=my_entry(bot, update, user_data))
    elif service == '2':
        info_tuple = tuple(info_list[4:8])
        new_tuple = info_tuple + (user_data.get('number'),)
        cursor.execute("DELETE FROM record_info WHERE"
                       " service = %s and name = %s and date = %s and time = %s and number = %s",
                       new_tuple)
        conn.commit()

        max_entries.pop()

        if len(job_list) == 2:
            print('убрали второй джоб и джоба было 2')
            job_list[1].schedule_removal()
        if len(info_list) == 12:
            print('убрали второй джоб')
            job_list[1].schedule_removal()
        if len(info_list) == 8 and len(job_list) == 3:
            print('убрали третий джоб')
            job_list[2].schedule_removal()
        bot.edit_message_reply_markup(chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id,
                                      reply_markup=my_entry(bot, update, user_data))
    elif service == '3':
        info_tuple = tuple(info_list[8:12])
        new_tuple = info_tuple + (user_data.get('number'),)
        cursor.execute("DELETE FROM record_info WHERE"
                       " service = %s and name = %s and date = %s and time = %s and number = %s",
                       new_tuple)
        conn.commit()

        max_entries.pop()

        if len(info_list) == 12:
            print('убрали третий джоб')
            job_list[2].schedule_removal()
        bot.send_message(chat_id=update.callback_query.from_user.id,
                         text='Есть!',
                         reply_markup=my_entry(bot, update, user_data))
    elif service == 'Отмена':
        info_tuple = user_data.get('number')
        cursor.execute("DELETE FROM record_info WHERE number = %s" % info_tuple)

        user_data.clear()
        max_entries.clear()

        conn.commit()
        job_queue.stop()
        bot.delete_message(chat_id=update.callback_query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(chat_id=update.callback_query.from_user.id,
                         text='У вас нет записей {} '.format(smiles[9]),
                         reply_markup=start_keyboard)
    elif service == '0':
        bot.delete_message(chat_id=update.callback_query.from_user.id,
                           message_id=query.message.message_id)
        bot.send_message(chat_id=update.callback_query.from_user.id,
                         text='Вы вернулись в главное меню',
                         reply_markup=start_keyboard)


def info(bot, update):
    update.message.reply_text("Наши контакты: \n "
                              "Адрес: г.Москва \n "
                              "Телефон: +74951234567 \n "
                              "Часы работы: \n "
                              "Будни: с 10:00 до 22:00 \n "
                              "Выходные: c 10:00 до 22:00",
                              reply_markup=menu_keyboard)


def main():
    mybot = Updater("728852231:AAEZLnITK0BYNpAfQ4DCIC8CjpyiYLYUpIo", request_kwargs=PROXY)

    dp = mybot.dispatcher
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default = True

    conv_handler = ConversationHandler(
        entry_points=[RegexHandler('Добавить запись', choose_room, pass_user_data=True),
                      RegexHandler('Парикмахерский зал', choose_service, pass_user_data=True),
                      RegexHandler('Маникюрный зал', choose_service, pass_user_data=True),
                      RegexHandler('Мои записи', my_entry, pass_user_data=True)],
        states={FIRST: [CallbackQueryHandler(choose_master, pass_user_data=True)],
                SECOND: [CallbackQueryHandler(calendar, pass_user_data=True)],
                THIRD: [CallbackQueryHandler(time_check, pass_user_data=True)],
                FOURTH: [CallbackQueryHandler(contact, pass_user_data=True)],
                FIVE: [CallbackQueryHandler(cancel_entries, pass_user_data=True, pass_job_queue=True)]},
        fallbacks=[MessageHandler(Filters.contact, get_contact, pass_user_data=True, pass_job_queue=True)],
        allow_reentry=True)

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", greet_user, pass_user_data=True))
    dp.add_handler(CommandHandler("Вернуться в главное меню", greet_user, pass_user_data=True))
    dp.add_handler(RegexHandler("Вернуться в главное меню", greet_user, pass_user_data=True))
    dp.add_handler(CommandHandler("О нас", info))
    dp.add_handler(RegexHandler("О нас", info))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()

'''Сделать чтобы напоминания приходили за сутки (за час)'''
