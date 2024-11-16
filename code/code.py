#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import telebot
import time
import helper
import edit
import history
import display
import estimate
import delete
import add
import budget
import category
import extract
import sendEmail
import add_recurring
import income
import receipt
from datetime import datetime
from jproperties import Properties

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
# import sendEmailStats
import setReminder


configs = Properties()

with open('user.properties', 'rb') as read_prop:
    configs.load(read_prop)

api_token = str(configs.get('api_token').data)

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)

option = {}


# Define listener for requests by user
def listener(user_requests):
    for req in user_requests:
        if (req.content_type == 'text'):
            print("{} name:{} chat_id:{} \nmessage: {}\n".format(
                str(datetime.now()), str(req.chat.first_name), str(req.chat.id), str(req.text)))


bot.set_update_listener(listener)


# defines how the /start and /menu commands have to be handled/processed
@bot.message_handler(commands=['start', 'menu'])
def start_and_menu_command(m):
    helper.read_json()
    global user_list
    chat_id = m.chat.id

    text_intro = "Welcome to MyDollarBot - a simple solution to track your expenses and manage them! \n Please select the options from below for me to assist you with: \n\n"
    commands = helper.getCommands()
    for c in commands:  # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n\n"
    bot.send_message(chat_id, text_intro)
    return True


# defines how the /add command has to be handled/processed
@bot.message_handler(commands=['add'])
def command_add(message):
    add.run(message, bot)


# function to add recurring expenses
@bot.message_handler(commands=['add_recurring'])
def command_add_recurring(message):
    add_recurring.run(message, bot)


# function to fetch expenditure history of the user
@bot.message_handler(commands=['history'])
def command_history(message):
    history.run(message, bot)


# function to edit date, category or cost of a transaction
@bot.message_handler(commands=['edit'])
def command_edit(message):
    edit.run(message, bot)


# function to display total expenditure
@bot.message_handler(commands=['display'])
def command_display(message):
    display.run(message, bot)


# function to estimate future expenditure
@bot.message_handler(commands=['estimate'])
def command_estimate(message):
    estimate.run(message, bot)


# handles "/delete" command
@bot.message_handler(commands=['delete'])
def command_delete(message):
    delete.run(message, bot)


@bot.message_handler(commands=['budget'])
def command_budget(message):
    budget.run(message, bot)


@bot.message_handler(commands=['category'])
def command_category(message):
    category.run(message, bot)


@bot.message_handler(commands=['extract'])
def command_extract(message):
    extract.run(message, bot)


@bot.message_handler(commands=['sendEmail'])
def command_sendEmail(message):
    sendEmail.run(message, bot)


@bot.message_handler(commands=['receipt'])
def command_receipt(message):
    receipt.command_receipt(message, bot)


# Calendar command to show transactions for a selected date
@bot.message_handler(commands=['calendar'])
def command_calendar(message):
    bot.send_message(message.chat.id, "Please select a date (format: YYYY-MM-DD):")


# Capture user input for the date
@bot.message_handler(func=lambda message: re.match(r'^\d{4}-\d{2}-\d{2}$', message.text))
def capture_date_input(message):
    try:
        selected_date = datetime.strptime(message.text, '%Y-%m-%d')
        bot.send_message(message.chat.id, f"Date {selected_date.date()} selected. Retrieving transactions...")
        helper.show_spend_for_date(selected_date, message.chat.id, bot)  # Call the helper function here
    except ValueError:
        bot.send_message(message.chat.id, "Invalid date format! Please use YYYY-MM-DD.")


@bot.message_handler(commands=['income'])
def command_income(message):
    income.set_income(message, bot)


# Capture the income input
@bot.message_handler(func=lambda message: message.text.isdigit())
def capture_income(message):
    income.process_income_input(message, bot)


@bot.message_handler(commands=['setRemind'])
def set_reminder(message):
    bot.reply_to(message, "Hello! Use /remind YYYY-MM-DD-HH:MM <Reminder Message> to set a reminder. Make sure to use the 24-hour format.")


# Reminder command
@bot.message_handler(commands=['remind'])
def reminder(message):
    setReminder.run_set_reminder(message, bot)



# not used
def addUserHistory(chat_id, user_record):
    global user_list
    if (not (str(chat_id) in user_list)):
        user_list[str(chat_id)] = []
    user_list[str(chat_id)].append(user_record)
    return user_list


def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.exception(str(e))
        time.sleep(3)
        print("Connection Timeout")


if __name__ == '__main__':
    main()

