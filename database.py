user_money = {}
user_items_db = {}
shop = []

def add_money(user_id, amount):
    """Добавить деньги пользователю"""
    if user_id not in user_money:
        user_money[user_id] = 0
    user_money[user_id] += amount

def get_user_items(user_id):
    """Получить предметы пользователя"""
    if user_id not in user_items_db:
        user_items_db[user_id] = []
    return user_items_db[user_id]

def get_user_money(user_id):
    """Получить деньги пользователя"""
    return user_money.get(user_id, 0)
