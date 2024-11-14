from datetime import datetime
import helper


# Function to filter and display transactions for a specific date
def show_spend_for_date(selected_date, chat_id, bot):
    transactions = helper.getUserHistory(chat_id)
    filtered_transactions = []

    # Filter transactions for the selected date
    for txn in transactions:
        txn_date = datetime.strptime(txn.split(',')[0], '%d-%b-%Y')
        if txn_date.date() == selected_date.date():
            filtered_transactions.append(txn)

    # Send the filtered transactions to the user
    if filtered_transactions:
        for txn in filtered_transactions:
            date, category, amount, _ = txn.split(',')
            bot.send_message(chat_id, f"{date} - {category}: ${amount}")
    else:
        bot.send_message(chat_id, "No transactions found for the selected date.")
