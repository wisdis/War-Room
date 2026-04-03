from storage import get_user_items, get_user_stats, add_money

def can_buy(member, item):
    if item["allowed_roles"]:
        if not any(role.id in item["allowed_roles"] for role in member.roles):
            return False
    if any(role.id in item["blocked_roles"] for role in member.roles):
        return False
    return True

def apply_item_effects_to_user(user_id, item):
    stats = get_user_stats(user_id)
    for key, value in item.get("buffs", {}).items():
        if key in stats:
            stats[key] += value
    for key, value in item.get("debuffs", {}).items():
        if key in stats:
            stats[key] += value

def give_income_to_member(member, role_income):
    income = 0
    for role in member.roles:
        if role.id in role_income:
            income += role_income[role.id].get("income", 0)
    stats = get_user_stats(member.id)
    income += stats.get("income", 0)
    if income > 0:
        add_money(member.id, income)
