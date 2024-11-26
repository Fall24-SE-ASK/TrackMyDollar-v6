import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib
from email import encoders
import os.path
import threading
import extract
import helper
import graphing
import time
from datetime import datetime
from telebot import types

extract_complete = threading.Event()



def calculate_spendings(queryResult, preferred_currency):
    total_dict = {}

    for row in queryResult:
        s = row.split(',')
        cat = s[1]  # Category
        amount = float(s[2])
        currency = s[3]  # Currency of the expense

        # Convert to preferred currency
        converted_amount = helper.convert_currency(amount, currency, preferred_currency)

        # Add the expense to the total for the category
        if cat in total_dict:
            total_dict[cat] = round(total_dict[cat] + converted_amount, 2)
        else:
            total_dict[cat] = converted_amount

    total_text = ""
    for key, value in total_dict.items():
        total_text += f"{key} {value:.2f} {preferred_currency}\n"

    return total_text




def display_total(message, bot):
    global total
    global bud

    selected_category = 'All'
    DayWeekMonth = 'Month'
        
    # print("---2----")

    try:
        chat_id = message.chat.id
        # DayWeekMonth = message.text

        if DayWeekMonth not in helper.getSpendDisplayOptions():
            raise Exception(f"Sorry I can't show spendings for \"{DayWeekMonth}\"!")

        history = helper.getUserHistory(chat_id)
        if history is None:
            raise Exception("Oops! Looks like you do not have any spending records!")

        bot.send_message(chat_id, "Hold on! Calculating...")
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(0.5)

        # Get user preferred currency
        preferred_currency = helper.get_user_preferred_currency(chat_id)

        # Filter the expenses based on the selected time period (Day or Month) and category
        queryResult = []
        if DayWeekMonth == 'Day':
            query = datetime.now().today().strftime(helper.getDateFormat())
            if selected_category == 'All':
                queryResult = [value for index, value in enumerate(history) if str(query) in value]
            else:
                queryResult = [value for index, value in enumerate(history) if str(query) in value and selected_category in value]
        elif DayWeekMonth == 'Month':
            query = datetime.now().today().strftime(helper.getMonthFormat())
            if selected_category == 'All':
                queryResult = [value for index, value in enumerate(history) if str(query) in value]
            else:
                queryResult = [value for index, value in enumerate(history) if str(query) in value and selected_category in value]

        # Check if there are no expenses in this category or all categories
        if not queryResult:
            if selected_category == 'All':
                remaining_budget = helper.getOverallRemainingBudget(chat_id)  # Get overall remaining budget for all categories
                bot.send_message(chat_id, f"No expenses recorded for all categories in {DayWeekMonth}. Remaining Amount: ${remaining_budget:.2f} (Income - Expenditure)")
            else:
                remaining_budget = helper.get_remaining_budget(chat_id, selected_category)
                bot.send_message(chat_id, f"No expenses recorded for {selected_category} in {DayWeekMonth}. Remaining Amount: ${remaining_budget:.2f} (Income - Expenditure)")
        else:
            # Calculate total spending in the category or all categories
            total_text = calculate_spendings(queryResult, preferred_currency)
            total = total_text

            if selected_category != 'All':
                bud = helper.getCategoryBudgetByCategory(chat_id, selected_category)
            else:
                bud = helper.getOverallBudget(chat_id)  # Get overall budget for all categories

            spending_text = f"Here are your total spendings for {selected_category} in {DayWeekMonth.lower()}:\nCATEGORIES, AMOUNT \n----------------------\n{total_text}"
            bot.send_message(chat_id, spending_text)

            # Show remaining balance
            if selected_category == 'All':
                 remaining_budget = helper.get_remaining_budget(chat_id, selected_category)
            else:
                remaining_budget = helper.get_remaining_budget(chat_id, 'All')

            bot.send_message(chat_id, f"Remaining Amount: ${remaining_budget:.2f}")

            # Ask the user if they want to see a plot
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.row_width = 2
            for plot in helper.getplot():
                markup.add(plot)
            
            # msg = bot.reply_to(message, 'Please select a plot to see the total expense', reply_markup=markup)
            print("--------kk22-----")
            graphing.visualize(total, bud)
            print("--------kk3------")
            
            # bot.register_next_step_handler(msg, plot_total, bot)

    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, str(e))


# def plot_total(message, bot):
#     chat_id = message.chat.id
#     pyi = message.text
#     if pyi == 'Bar with budget':
#     graphing.visualize(total, bud)
#     bot.send_photo(chat_id, photo=open('expenditure.png', 'rb'))
#         os.remove('expenditure.png')
#     elif pyi == 'Bar without budget':
#         graphing.viz(total)
#         bot.send_photo(chat_id, photo=open('expend.png', 'rb'))
#         # os.remove('expend.png')
#     else:
#         graphing.vis(total)
#         bot.send_photo(chat_id, photo=open('pie.png', 'rb'))
#         # os.remove('pie.png')





# Function to send an email
def send_email(user_email, subject, message, attachment_path):
    smtp_port = 587                 # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "dollarbot123@gmail.com"
    email_to = user_email
    pswd = "tsvueizeuvzivtjo"   # App password 

    # Make the body of the email
    body = message

    # make a MIME object to define parts of the email
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    # Attach the body of the message
    msg.attach(MIMEText(body, 'plain'))

    # Define the file to attach
    filename = attachment_path

    # Open the file in python as a binary
    attachment = open(filename, 'rb')  # r for read and b for binary

    # Encode as base 64
    attachment_package = MIMEBase('application', 'octet-stream')
    attachment_package.set_payload((attachment).read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
    msg.attach(attachment_package)

    # Cast as string
    text = msg.as_string()

        # Connect with the server
    print("Connecting to server...")
    TIE_server = smtplib.SMTP(smtp_server, smtp_port)
    TIE_server.starttls()
    TIE_server.login(email_from, pswd)
    print("Succesfully connected to server")
    print()

    # Send emails to "person" as list is iterated
    print(f"Sending email to: {email_to}...")
    TIE_server.sendmail(email_from, email_to, text)
    print(f"Email sent to: {email_to}")
    print()

    # Close the port
    TIE_server.quit()


# Function to run the main process
def run(message, bot):
    try:
        chat_id = message.chat.id
        
        message = bot.send_message(chat_id, 'Please enter your email: ')
        bot.register_next_step_handler(message, process_email_input, bot)        
    except Exception as e:
        logging.error(str(e))


# Function for sending all parameters to email
def process_email_input(message, bot):
    print("---1----")
    display_total(message, bot)  ##--
    try:
        chat_id = message.chat.id
        user_email = message.text

        # Compose the email
        email_subject = "DollarBot Budget Report"
        email_message = f"Hello {user_email},\n\nPFA the budget report that you requested."

        # Check if data.csv exists; if present send email, if not present call extract function and then send email
        check_file = os.path.isfile('expenditure.png')
        if check_file:
            send_email(user_email, email_subject, email_message, 'expenditure.png')
        else:
            file_path = extract.run(message, bot)
            send_email(user_email, email_subject, email_message, file_path)

        message = bot.send_message(chat_id, 'Email sent successfully!') 

    except Exception as e:
        logging.error(str(e))




