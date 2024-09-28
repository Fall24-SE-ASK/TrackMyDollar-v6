import re
import json
import os
from datetime import datetime

# Supported currency conversion rates (manually defined)
conversion_rates = {
    ('USD', 'INR'): 83.0,
    ('INR', 'USD'): 0.012,
    ('USD', 'EUR'): 0.95,
    ('EUR', 'USD'): 1.05,
    ('INR', 'EUR'): 0.0114,
    ('EUR', 'INR'): 87.5,
}

choices = ['Date', 'Category', 'Cost']
plot = ['Bar with budget', 'Pie', 'Bar without budget']
spend_display_option = ['Day', 'Month']
spend_categories = ['Food', 'Groceries', 'Utilities', 'Transport', 'Shopping', 'Miscellaneous']
spend_estimate_option = ['Next day', 'Next month']
update_options = {
    'continue': 'Continue',
    'exit': 'Exit'
}

budget_options = {
    'update': 'Add/Update',
    'view': 'View',
    'max_spend': 'Transaction Max Spend Limit',
    'delete': 'Delete'
}

budget_types = {
    'overall': 'Overall Budget',
    'category': 'Category-Wise Budget',
}

data_format = {
    'data': [],
    'budget': {
        'overall': None,
        'category': None,
        'max_per_txn_spend': None
    }
}

category_options = {
    'add': 'Add',
    'delete': 'Delete',
    'view': 'Show Categories'
}

# Set of implemented commands and their descriptions
commands = {
    'menu': 'Display this menu',
    'add': 'Record/Add a new spending',
    'calendar': 'View transactions for a selected date',
    'add_recurring': 'Add a new recurring expense for future months',
    'display': 'Show sum of expenditure for the current day/month',
    'estimate': 'Show an estimate of expenditure for the next day/month',
    'history': 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details',
    'budget': 'Add/Update/View/Delete budget',
    'category': 'Add/Delete/Show custom categories',
    'extract': 'Extract data into CSV',
    'sendEmail': 'Email CSV to user',
    'receipt': 'Show the receipt for the day',
    'income': 'Add income for the month'
}

dateFormat = '%d-%b-%Y'
timeFormat = '%H:%M'
monthFormat = '%b-%Y'

# Function to convert currency
def convert_currency(amount, from_currency, to_currency):
    """Convert the given amount from one currency to another using predefined rates."""
    if from_currency == to_currency:
        return amount
    conversion_key = (from_currency, to_currency)
    if conversion_key in conversion_rates:
        return round(amount * conversion_rates[conversion_key], 2)
    else:
        raise ValueError(f"Unsupported currency conversion from {from_currency} to {to_currency}")

# Function to load .json expense record data
def read_json():
    try:
        if not os.path.exists('expense_record.json'):
            with open('expense_record.json', 'w') as json_file:
                json_file.write('{}')
            return {}
        elif os.stat('expense_record.json').st_size != 0:
            with open('expense_record.json') as expense_record:
                expense_record_data = json.load(expense_record)
            return expense_record_data
        else:
            return {}  # Return an empty dictionary if file is empty
    except FileNotFoundError:
        print("---------NO RECORDS FOUND---------")
        return {}

def write_json(user_list):
    try:
        with open('expense_record.json', 'w') as json_file:
            json.dump(user_list, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print('Sorry, the data file could not be found.')

def validate_entered_amount(amount_entered):
    if amount_entered is None:
        return 0
    if re.match("^[1-9][0-9]{0,14}\\.[0-9]*$", amount_entered) or re.match("^[1-9][0-9]{0,14}$", amount_entered):
        amount = round(float(amount_entered), 2)
        if amount > 0:
            return str(amount)
    return 0

# Validate duration (for recurring expenses)
def validate_entered_duration(duration_entered):
    if duration_entered is None:
        return 0
    if re.match("^[1-9][0-9]{0,14}", duration_entered):
        duration = int(duration_entered)
        if duration > 0:
            return str(duration)
    return 0

def get_help_text():
    return "Here is some help text."

# Set user income in the JSON record
def setUserIncome(chat_id, income_value):
    user_list = read_json()

    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = createNewUserRecord()

    user_list[str(chat_id)]['income'] = income_value
    write_json(user_list)

# Retrieve user data (income, transactions, etc.)
def getUserData(chat_id):
    user_data = read_json()
    if str(chat_id) in user_data:
        return user_data[str(chat_id)]
    else:
        return {}

# Calculate total expenditure for the current month
def calculate_total_expenditure(chat_id):
    transactions = getTransactionsForChat(chat_id)
    total_expenditure = 0.0
    for txn in transactions:
        txn_amount = float(txn.split(',')[2])  # Assuming amount is the third value in the transaction string
        total_expenditure += txn_amount
    return total_expenditure

# Validate if a transaction exceeds the transaction limit
def validate_transaction_limit(chat_id, amount_value, bot):
    if isMaxTransactionLimitAvailable(chat_id):
        maxLimit = round(float(getMaxTransactionLimit(chat_id)), 2)
        if round(float(amount_value), 2) >= maxLimit:
            bot.send_message(chat_id, 'Warning! You went over your transaction spend limit.')

# Check if the new transaction exceeds user's monthly income
def checkIfExceedsIncome(chat_id, amount_to_add, bot):
    income = getIncome(chat_id)
    if income is None:
        bot.send_message(chat_id, "You haven't set your monthly income. Please set your income using /income.")
        return True  # No income set, block the transaction

    total_spend = getTotalSpendForMonth(chat_id)
    if total_spend + amount_to_add > float(income):
        bot.send_message(chat_id, f"Transaction exceeds your monthly income limit! You have spent ${total_spend}, which exceeds your income of ${income}.")
        return True

    return False

# Various utility functions
def getUserHistory(chat_id):
    data = getUserData(chat_id)
    if data is not None:
        return data['data']
    return None

def createNewUserRecord():
    return data_format

def getOverallBudget(chat_id):
    data = getUserData(chat_id)
    return data['budget']['overall'] if data else None

def getCategoryBudget(chat_id):
    data = getUserData(chat_id)
    return data['budget']['category'] if data else None

def getMaxTransactionLimit(chat_id):
    data = getUserData(chat_id)
    return data['budget']['max_per_txn_spend'] if data else None

def isOverallBudgetAvailable(chat_id):
    return getOverallBudget(chat_id) is not None

def isMaxTransactionLimitAvailable(chat_id):
    return getMaxTransactionLimit(chat_id) is not None

def display_remaining_budget(message, bot, cat):
    chat_id = message.chat.id
    if isOverallBudgetAvailable(chat_id):
        display_remaining_overall_budget(message, bot)
    elif isCategoryBudgetByCategoryAvailable(chat_id, cat):
        display_remaining_category_budget(message, bot, cat)

# Display remaining overall budget
def display_remaining_overall_budget(message, bot):
    chat_id = message.chat.id
    remaining_budget = calculateRemainingOverallBudget(chat_id)
    if remaining_budget >= 0:
        msg = f'Remaining Overall Budget is ${remaining_budget}'
    else:
        msg = f'Budget Exceeded! Expenditure exceeds the budget by ${abs(remaining_budget)}'
    bot.send_message(chat_id, msg)

# Remaining category budget
def display_remaining_category_budget(message, bot, cat):
    chat_id = message.chat.id
    remaining_budget = calculateRemainingCategoryBudget(chat_id, cat)
    if remaining_budget >= 0:
        msg = f'Remaining Budget for {cat} is ${remaining_budget}'
    else:
        msg = f'Budget for {cat} Exceeded! Expenditure exceeds the budget by ${abs(remaining_budget)}'
    bot.send_message(chat_id, msg)

def isCategoryBudgetByCategoryAvailable(chatId, category):
    """
    Check if the category budget is available for a specific category.
    """
    data = getCategoryBudget(chatId)
    if data is None:
        return False
    return category in data.keys()


def get_user_preferred_currency(chat_id):
    """
    Retrieve the user's preferred currency. For simplicity, let's assume it's stored in the user record.
    """
    user_data = getUserData(chat_id)
    return user_data.get('preferred_currency', 'USD')  # Default to USD if not set


# Functions for handling categories, budgets, and transactions

def getSpendCategories():
    with open("categories.txt", "r") as tf:
        spend_categories = tf.read().split(',')
    return spend_categories

def getplot():
    return plot

def getSpendDisplayOptions():
    return spend_display_option

def getSpendEstimateOptions():
    return spend_estimate_option

def getCommands():
    return commands

def getDateFormat():
    return dateFormat

def getTimeFormat():
    return timeFormat

def getMonthFormat():
    return monthFormat

def getChoices():
    return choices

def getBudgetOptions():
    return budget_options

def getBudgetTypes():
    return budget_types

def getUpdateOptions():
    return update_options

def getCategoryOptions():
    return category_options

