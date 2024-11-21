import re
import json
import os
import urllib.request
import certifi
import ssl
from datetime import date
from currency_converter import SINGLE_DAY_ECB_URL, CurrencyConverter


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
    'income': 'Add income for the month',
    'currencies': 'Show the list of currencies supported'
}

dateFormat = '%d-%b-%Y'
timeFormat = '%H:%M'
monthFormat = '%b-%Y'


def throw_exception(e, message, bot, logging):
    logging.error(f"An exception occurred: {e}")
    bot.send_message(message.chat.id, str(e))


def getTransactionsForChat(chat_id):
    user_data = read_json()
    if str(chat_id) in user_data:
        return user_data[str(chat_id)].get('data', [])
    return []

def get_currency_converter():
    currency_file_name = f"ecb_{date.today():%Y%m%d}.zip"
    if not os.path.isfile(currency_file_name):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(SINGLE_DAY_ECB_URL, context=ssl_context) as response, open(currency_file_name, "wb") as out_file:
            out_file.write(response.read())
    c = CurrencyConverter(currency_file_name)
    return c

# Function to convert currency
def convert_currency(amount, from_currency, to_currency):
    """Convert the given amount from one currency to another using the rates fetched for that day."""
    if from_currency == to_currency:
        return amount
    
    c = get_currency_converter()
    if from_currency in c.currencies and to_currency in c.currencies:
        return round(c.convert(amount, from_currency, to_currency), 2)
    else:
        raise ValueError(f"Unsupported currency conversion from {from_currency} to {to_currency}")

def get_currencies():
    "Returns the list of currencies supported by the bot"
    c = get_currency_converter()
    return sorted(c.currencies)

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
def calculate_total_expenditure(chat_id, category=None):
    user_data = getUserData(chat_id)
    
    if not user_data or 'data' not in user_data:
        return 0.0

    total_expenditure = 0.0

    # Loop through the user's spending records
    for record in user_data['data']:
        record_data = record.split(',')
        record_category = record_data[1]
        record_amount = float(record_data[2])
        
        # If a category is provided, only sum expenses for that category
        if category is None or record_category == category:
            total_expenditure += record_amount

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
    preferred_currency = get_user_preferred_currency(chat_id)  # Retrieve preferred currency
    
    if income is None:
        bot.send_message(chat_id, "You haven't set your monthly income. Please set your income using /income.")
        return True  # No income set, block the transaction

    # Ensure amount_to_add is converted to the user's preferred currency
    converted_amount = convert_currency(amount_to_add, 'USD', preferred_currency)  # Convert to USD or any base

    total_spend = getTotalSpendForMonth(chat_id)  # Ensure total spend is also in the same currency
    if total_spend + converted_amount > float(income):
        bot.send_message(chat_id, f"Transaction exceeds your monthly income limit! You have spent ${total_spend}, which exceeds your income of ${income}.")
        return True

    return False

def get_remaining_budget(chat_id, selected_category):
    # Get the user's total income
    user_data = getUserData(chat_id)
    if 'income' not in user_data:
        return 0.0  # No income set

    income = float(user_data['income'])

    # Calculate the total expenditure across all categories
    total_expenditure = calculate_total_expenditure(chat_id)  # Sum of all categories

    # Calculate the remaining budget as income minus total expenditure
    remaining_budget = income - total_expenditure

    return remaining_budget



def getOverallRemainingBudget(chat_id):
    user_data = getUserData(chat_id)
    total_expenditure = calculate_total_expenditure(chat_id)
    
    if 'income' not in user_data or user_data['income'] == 0:
        return None  # No income set yet

    remaining_budget = user_data['income'] - total_expenditure
    return remaining_budget

def getCategoryBudgetByCategory(chat_id, category):
    user_data = getUserData(chat_id)

    # Check if there is a category-specific budget
    if 'budgets' in user_data and category in user_data['budgets']:
        return user_data['budgets'][category]

    # Default to overall budget if no specific category budget exists
    return getOverallRemainingBudget(chat_id)


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

