# database.py

# Список всех предметов в магазине
shop = []

# Предметы каждого пользователя
# Формат: {user_id: [item_dict, ...]}
user_items = {}

# Баланс пользователей
# Формат: {user_id: int}
user_balance = {}

# Дополнительные параметры пользователя: доход, население, стабильность
# Формат: {user_id: {"income": int, "population": int, "stability": int}}
user_stats = {}

# Добавляем или снимаем деньги
def add_money(user_id, amount):
    if user_id not in user_balance:
        user_balance[user_id] = 0
    user_balance[user_id] += amount
    if user_balance[user_id] < 0:
        user_balance[user_id] = 0

# Получаем баланс
def get_balance(user_id):
    return user_balance.get(user_id, 0)

# Получаем список предметов пользователя
def get_user_items(user_id):
    return user_items.get(user_id, [])

# Применяем эффекты предмета (баффы/дебаффы)
def apply_item_effects(user_id, item):
    if user_id not in user_items:
        user_items[user_id] = []
    user_items[user_id].append(item)

    # Инициализируем stats, если нет
    if user_id not in user_stats:
        user_stats[user_id] = {"income": 0, "population": 0, "stability": 0}

    # Применяем баффы
    for key, value in item.get("buffs", {}).items():
        if key in user_stats[user_id]:
            user_stats[user_id][key] += value

    # Применяем дебаффы
    for key, value in item.get("debuffs", {}).items():
        if key in user_stats[user_id]:
            user_stats[user_id][key] += value  # дебаффы могут быть отрицательными

# Получаем текущие stats пользователя (для начисления дохода)
def get_user_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {"income": 0, "population": 0, "stability": 0}
    return user_stats[user_id]
