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
import sendEmailStats
import code


# Initialize the APScheduler
scheduler = BackgroundScheduler()
scheduler.start()


def run_set_reminder(message, bot):
    try:
        # Parse time from the message
        parts = message.text.split(maxsplit=2)  # Split into at most 3 parts: command, datetime, and reminder message
        # _, time_str, *reminder_message = message.text.split(maxsplit=2)     # Process '/remind 15:30' command. The /remind is stored in a throwaway _. The 15:30 is stored in time_str.  # maxsplit is a named argument to the split() function, that determines the maximum number of splits to perform ## *reminder_message is used to capture the remaining parts of the split text as a list.
        
        if len(parts) < 2:
            # Not enough parts provided
            bot.reply_to(message, "Invalid format! Use /remind YYYY-MM-DD-HH:MM <optional message>.")
            return
        

        # _, date_str, time_str, *reminder_message = parts

        _, datetime_str, reminder_message = parts


        # full_time_str = date_str + " " + time_str

        reminder_datetime = datetime.strptime(datetime_str, "%Y-%m-%d-%H:%M")   #string parse time: converts the time string and store in %H:%M format. .time() will extract only the time, leaving out the date part. NOTE:::: This will not work for reminders on other days 



        # Calculate the datetime for the reminder
        now = datetime.now()
        # reminder_datetime = datetime.combine(now.date(), reminder_time)    # combines date and time object into a single datetime object
        
        if reminder_datetime <= now:
            bot.reply_to(message, "You cannot set a reminder in the past, please set a later time")
            return

        reminder_message = "".join(reminder_message) if reminder_message else "It's time!"  # Default message if none is provided

        
        print(reminder_datetime)

        # Schedule the reminder
        scheduler.add_job(
            func=send_reminder,
            trigger=DateTrigger(run_date=reminder_datetime),     # Trigger when system time (run_date) equals the reminder_datetime
            args=[message.chat.id, reminder_message, bot],    # Chat id is passed to the send_reminder function so that this function knows which chat it has to use
            id=f"reminder_{message.chat.id}_{reminder_datetime}",   # Create a unique job_id string that can be used later
            replace_existing=True   # this job will replace if there is another job with the same id
        )

        bot.reply_to(message, f"Reminder set for {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')} for {reminder_message}")
    
    except (ValueError, IndexError):
        bot.reply_to(message, "Invalid format! Use /remind YYYY-MM-DD HH:MM (24-hour format).")


# Function to send the reminder
def send_reminder(chat_id, reminder_message, bot):
    bot.send_message(chat_id, f"Reminder: {reminder_message}")