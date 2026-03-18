import discord
from discord.ext import commands
import os
import random
import asyncio
from database import add_money, get_user_items, shop, get_balance, apply_item_effects

# токен
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

role_income = {}

@bot.event
async def on_ready():
    print(f'Бот {bot.user} готов к работе')
    bot.loop.create_task(give_income())

@bot.command()
async def привет(ctx):
    ответы = [
        "Привет!",
        "Приветствую!",
        "Добрый день 👋",
        "Здравствуйте!",
        "Салют!",
        "Хай!"
    ]
    await ctx.send(random.choice(ответы))

async def give_income():
    while True:
        for guild in bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                income = 0
                for role in member.roles:
                    if role.id in role_income:
                        income += role_income[role.id]["income"]

                items = get_user_items(member.id)
                for item in items:
                    income += item.get("income", 0)

                add_money(member.id, income)

        await asyncio.sleep(60)

@bot.command()
async def add_item(ctx):
    await ctx.send("Название предмета?")
    name = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Цена?")
    price = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    try:
        price_value = int(price.content)
    except:
        await ctx.send("Введите число")
        return

    await ctx.send("Описание (или 'Skip')")
    desc = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Разрешённые роли (через пробел, или 'everyone')?")
    allowed = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    allowed_roles = []
    if allowed.content.lower() != "everyone":
        for role in ctx.guild.roles:
            if role.name in allowed.content.split():
                allowed_roles.append(role.id)

    await ctx.send("Запрещённые роли (через пробел, или 'none')?")
    blocked = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    blocked_roles = []
    if blocked.content.lower() != "none":
        for role in ctx.guild.roles:
            if role.name in blocked.content.split():
                blocked_roles.append(role.id)

    # Баффы
    buffs = {}
    debuffs = {}

    await ctx.send("Баффы через запятую (income=10,population=5,stability=2) или 'skip'?")
    buff_input = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    if buff_input.content.lower() != "skip":
        for pair in buff_input.content.split(","):
            key, value = pair.split("=")
            buffs[key.strip()] = int(value.strip())

    await ctx.send("Дебаффы через запятую (income=-5,population=-2,stability=-1) или 'skip'?")
    debuff_input = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    if debuff_input.content.lower() != "skip":
        for pair in debuff_input.content.split(","):
            key, value = pair.split("=")
            debuffs[key.strip()] = int(value.strip())

    item = {
        "name": name.content,
        "price": price_value,
        "description": None if desc.content.lower() == "skip" else desc.content,
        "allowed_roles": allowed_roles,
        "blocked_roles": blocked_roles,
        "buffs": buffs,
        "debuffs": debuffs
    }

    shop.append(item)
    await ctx.send(f"Предмет {item['name']} создан")

def can_buy(member, item):
    if item["allowed_roles"]:
        if not any(role.id in item["allowed_roles"] for role in member.roles):
            return False
    if any(role.id in item["blocked_roles"] for role in member.roles):
        return False
    return True

@bot.command()
async def buy(ctx, *, item_name):
    # ищем предмет
    item = next((i for i in shop if i["name"].lower() == item_name.lower()), None)
    if not item:
        await ctx.send("Такого предмета нет")
        return

    if not can_buy(ctx.author, item):
        await ctx.send("Вы не можете купить этот предмет")
        return

    balance = get_balance(ctx.author.id)
    if balance < item["price"]:
        await ctx.send("У вас недостаточно денег")
        return

    add_money(ctx.author.id, -item["price"])  # списываем деньги
    apply_item_effects(ctx.author.id, item)   # применяем эффекты (баффы/дебаффы)

    await ctx.send(f"Вы купили {item['name']}")

@bot.command()
async def setup_role(ctx, action: str, role: discord.Role, income: int = 0, population: int = 0, stability: int = 0):
    action = action.lower()
    if action == "add":
        role_income[role.id] = {
            "income": income,
            "population": population,
            "stability": stability
        }
        await ctx.send(f"Роль {role.name} добавлена")
    elif action == "remove":
        if role.id in role_income:
            del role_income[role.id]
            await ctx.send(f"Роль {role.name} удалена")
        else:
            await ctx.send("Роль не найдена")

bot.run(TOKEN)
