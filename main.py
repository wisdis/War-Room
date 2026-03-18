import discord
from discord.ext import commands
import os
import random
import asyncio
from database import add_money, get_user_items, shop

# токен
TOKEN = os.getenv("TOKEN")

# intents
intents = discord.Intents.default()
intents.message_content = True  # важно для работы команд

# Префикс и intents
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    privet = [
        "Привет!",
        "Приветствую!",
        "Добрый день 👋",
        "Здравствуйте!",
        "Салют!",
        "Хай!"
    ]
    await ctx.send(random.choice(privet))

async def give_income():
    while True:
        for guild in bot.guilds:
            for member in guild.members:
                income = 0

                # доход от ролей
                for role in member.roles:
                    if role.id in role_income:
                        income += role_income[role.id]["Доход"]

                # доход от предметов
                user_items = get_user_items(member.id)
                for item in user_items:
                    income += item["income_bonus"]

                add_money(member.id, income)

        await asyncio.sleep(60)
      
@bot.command()
async def additem(ctx):
    await ctx.send("Название предмета?")
    name = await bot.wait_for("message", check=lambda m: m.author == ctx.author)

    await ctx.send("Цена?")
    price = await bot.wait_for("message", check=lambda m: m.author == ctx.author)

    await ctx.send("Описание или Skip")
    desc = await bot.wait_for("message", check=lambda m: m.author == ctx.author)

    item = {
        "название": name.content,
        "цена": int(price.content),
        "описание": None if desc.content == "Skip" else desc.content,
        "разрешённая роль": [],
        "запрещённая роль": [],
        "баффы": {},
        "дебаффы": {}
    }

    shop.append(item)
    await ctx.send("Предмет создан")


def can_buy(member, item):
    if item["allowed_roles"]:
        if not any(role.id in item["allowed_roles"] for role in member.roles):
            return False

    if any(role.id in item["blocked_roles"] for role in member.roles):
        return False

    return True

role_income = {}

@bot.command()
async def setup_role(ctx, action: str, role: discord.Role, income: int = 0, population: int = 0, stability: int = 0):
    
    if action == "add":
        role_income[role.id] = {
            "Доход": income,
            "Население": population,
            "Стабильность": stability
        }
        await ctx.send("Роль добавлена")

    elif action == "remove":
        if role.id in role_income:
            del role_income[role.id]
            await ctx.send("Роль удалена")
        else:
            await ctx.send("Роль не найдена")

bot.run(TOKEN)
