# database.py
shop = []  # список всех предметов
user_items = {}  # предметы каждого пользователя
user_balance = {}  # баланс каждого пользователя

def add_money(user_id, amount):
    if user_id not in user_balance:
        user_balance[user_id] = 0
    user_balance[user_id] += amount

def get_balance(user_id):
    return user_balance.get(user_id, 0)

def get_user_items(user_id):
    return user_items.get(user_id, [])

def apply_item_effects(user_id, item):
    if user_id not in user_items:
        user_items[user_id] = []
    user_items[user_id].append(item)
    
    # баффы/дебаффы можно хранить или применять
    # например, если хочешь хранить общий доход от предметов, то пока просто добавляем их в список
