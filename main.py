import telebot
from datetime import datetime, timedelta
import json

bot = telebot.TeleBot('TOKEN')

# Hard-coded categories for expenses
expense_categories = ['food', 'transport', 'entertainment', 'bills', 'clothes']

# Data structure to store income and expenses
data = {
    'income': [],
    'expenses': []
}

# Load data from file if it exists
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    pass


def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hello! This is a simple bot to help you manage your income and expenses. '
                                      'You can add expenses by specifying a category, '
                                      'view statistics of income and expenses by category for the day, '
                                      'month, week, and year, and more.')


@bot.message_handler(commands=["help"])
def help(message):

    user_id = message.from_user.id

    bot.send_message(user_id, "This is what I can do:\n"
                              "/add_expense - add expenses by specifying a category\n"
                              "/add_income - add income by specifying the income category\n"
                              "/view_expenses - view all expenses\n"
                              "/view_income - view all incomes\n"
                              "/delete_expense - remove costs\n"
                              "/delete_income - remove income\n"
                              "/stats - view income and expenditure statistics by categories for the day, "
                              "month, week and year.\n"
                              "/help - show instructions")


@bot.message_handler(commands=['categories'])
def categories_message(message):
    bot.send_message(message.chat.id, 'Available expense categories: ' + ', '.join(expense_categories))


@bot.message_handler(commands=['add_expense'])
def add_expense_message(message):
    msg = bot.send_message(message.chat.id, 'Please enter the amount and category of '
                                            'the expense in the format "amount category". '
                                            'For example: "10 food".')
    bot.register_next_step_handler(msg, process_add_expense)


def process_add_expense(message):
    try:
        amount, category = message.text.split()
        amount = float(amount)
        if category not in expense_categories:
            bot.send_message(message.chat.id, 'Invalid category. Please use one of the following '
                                              'categories: ' + ', '.join(expense_categories))
            return
        data['expenses'].append({
            'amount': amount,
            'category': category,
            'timestamp': datetime.now().timestamp()
        })
        save_data()
        bot.send_message(message.chat.id, 'Expense added successfully.')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the amount and category '
                                          'of the expense in the format "amount category". '
                                          'For example: "10 food".')


@bot.message_handler(commands=['add_income'])
def add_income_message(message):
    msg = bot.send_message(message.chat.id, 'Please enter the amount and category of the income in the '
                                            'format "amount category". For example: "100 salary".')
    bot.register_next_step_handler(msg, process_add_income)


def process_add_income(message):
    try:
        amount, category = message.text.split()
        amount = float(amount)
        data['income'].append({
            'amount': amount,
            'category': category,
            'timestamp': datetime.now().timestamp()
        })
        save_data()
        bot.send_message(message.chat.id, 'Income added successfully.')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the amount and '
                                          'category of the income in the format "amount category". '
                                          'For example: "100 salary".')


@bot.message_handler(commands=['view_expenses'])
def view_expenses_message(message):
    if not data['expenses']:
        bot.send_message(message.chat.id, 'No expenses found.')
        return
    expenses_str = ''
    total = 0
    for expense in data['expenses']:
        dt = datetime.fromtimestamp(expense['timestamp'])
        expenses_str += f"{dt.strftime('%Y-%m-%d %H:%M:%S')} - {expense['category']} - {expense['amount']}\n"
        total += expense['amount']
    expenses_str += f"Total: {total}"
    bot.send_message(message.chat.id, expenses_str)


@bot.message_handler(commands=['view_income'])
def view_income_message(message):
    if not data['income']:
        bot.send_message(message.chat.id, 'No income found.')
        return
    income_str = ''
    total = 0
    for income in data['income']:
        dt = datetime.fromtimestamp(income['timestamp'])
        income_str += f"{dt.strftime('%Y-%m-%d %H:%M:%S')} - {income['category']} - {income['amount']}\n"
        total += income['amount']
    income_str += f"Total: {total}"
    bot.send_message(message.chat.id, income_str)


@bot.message_handler(commands=['delete_expense'])
def delete_expense_message(message):
    if not data['expenses']:
        bot.send_message(message.chat.id, 'No expenses found.')
        return
    msg = bot.send_message(message.chat.id, 'Please enter the index of the expense you want to delete. '
                                            'For example: "1".')
    bot.register_next_step_handler(msg, process_delete_expense)


def process_delete_expense(message):
    try:
        index = int(message.text) - 1
        if index < 0 or index >= len(data['expenses']):
            bot.send_message(message.chat.id, 'Invalid index.')
            return
        del data['expenses'][index]
        save_data()
        bot.send_message(message.chat.id, 'Expense deleted successfully.')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the index of the expense you want to delete. '
                                          'For example: "1".')


@bot.message_handler(commands=['delete_income'])
def delete_income_message(message):
    if not data['income']:
        bot.send_message(message.chat.id, 'No income found.')
        return
    msg = bot.send_message(message.chat.id, 'Please enter the index of the income you want to delete. '
                                            'For example: "1".')
    bot.register_next_step_handler(msg, process_delete_income)


def process_delete_income(message):
    try:
        index = int(message.text) - 1
        if index < 0 or index >= len(data['income']):
            bot.send_message(message.chat.id, 'Invalid index.')
            return
        del data['income'][index]
        save_data()
        bot.send_message(message.chat.id, 'Income deleted successfully.')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the index of the income you want to '
                                          'delete. For example: "1".')


@bot.message_handler(commands=['stats'])
def stats_message(message):
    msg = bot.send_message(message.chat.id, 'Please enter the time period and category for which '
                                            'you want to view statistics. Time period can be one of '
                                            '"day", "week", "month", or "year". Category can be one of '
                                            'the available expense categories or "all" for all categories. '
                                            'For example: "month food".')
    bot.register_next_step_handler(msg, process_stats)


def process_stats(message):
    try:
        time_period, category = message.text.split()
        if time_period not in ['day', 'week', 'month', 'year']:
            bot.send_message(message.chat.id, 'Invalid time period. Please use one of the following '
                                              'time periods: day, week, month, year.')
            return
        if category != 'all' and category not in expense_categories:
            bot.send_message(message.chat.id, 'Invalid category. Please use one of the following categories: '
                                              'all, ' + ', '.join(expense_categories))
            return

        now = datetime.now()
        if time_period == 'day':
            start_timestamp = now.replace(hour=0, minute=0, second=0).timestamp()
        elif time_period == 'week':
            start_timestamp = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0).timestamp()
        elif time_period == 'month':
            start_timestamp = now.replace(day=1, hour=0, minute=0, second=0).timestamp()
        else:
            start_timestamp = now.replace(month=1, day=1, hour=0, minute=0, second=0).timestamp()

        income_total = 0
        expenses_total = 0
        for income in data['income']:
            if income['timestamp'] >= start_timestamp and (category == 'all' or income['category'] == category):
                income_total += income['amount']
        for expense in data['expenses']:
            if expense['timestamp'] >= start_timestamp and (category == 'all' or expense['category'] == category):
                expenses_total += expense['amount']

        stats_str = f"Income for {time_period}: {income_total}\nExpenses for {time_period}: " \
                    f"{expenses_total}\nNet for {time_period}: {income_total - expenses_total}"
        bot.send_message(message.chat.id, stats_str)
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the time period and category for '
                                          'which you want to view statistics. Time period can be one of "day", '
                                          '"week", "month", or "year". Category can be one of the available expense '
                                          'categories or "all" for all categories. For example: "month food".')


def run():
    bot.polling()


if __name__ == '__main__':
    run()

