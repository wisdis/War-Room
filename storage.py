# данные
shop_items = []
user_items = {}      # {user_id: [item_dict, ...]}
user_balance = {}    # {user_id: int}
user_stats = {}      # {user_id: {"income": int, "population": int, "stability": int}}

# функции
def add_money(user_id, amount):
    if user_id not in user_balance:
        user_balance[user_id] = 0
    user_balance[user_id] += amount
    if user_balance[user_id] < 0:
        user_balance[user_id] = 0

def get_balance(user_id):
    return user_balance.get(user_id, 0)

def get_user_items(user_id):
    return user_items.get(user_id, [])

def get_user_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {"income": 0, "population": 0, "stability": 0}
    return user_stats[user_id]

def apply_item_effects(user_id, item):
    if user_id not in user_items:
        user_items[user_id] = []
    user_items[user_id].append(item)

    stats = get_user_stats(user_id)

    for key, value in item.get("buffs", {}).items():
        if key in stats:
            stats[key] += value

    for key, value in item.get("debuffs", {}).items():
        if key in stats:
            stats[key] += value

def add_item_to_shop(item):
    shop_items.append(item)

def can_buy(member_roles, item):
    allowed_roles = item.get("allowed_roles", [])
    blocked_roles = item.get("blocked_roles", [])

    if allowed_roles and not any(role in allowed_roles for role in member_roles):
        return False
    if any(role in blocked_roles for role in member_roles):
        return False
    return True
