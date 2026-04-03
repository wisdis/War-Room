import discord
from discord.ext import commands, tasks
import os
import asyncio
from storage import get_user_stats, add_money, role_income

TOKEN = os.getenv("TOKEN")
PREFIX = "."

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ==================== ЗАГРУЗКА КОМАНД ====================
async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"commands.{filename[:-3]}")
                print(f"✅ Загружен: commands.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Ошибка при загрузке commands.{filename[:-3]} → {e}")

# ==================== SETUP HOOK ====================
@bot.event
async def setup_hook():
    await load_extensions()
    print("Все расширения (cogs) успешно загружены!")

# ==================== ON READY ====================
@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов")
    if not give_income.is_running():
        give_income.start()

# ==================== ОБРАБОТКА ОШИБОК ====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Пропущен аргумент. Пример: .{ctx.command} <аргументы>")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Неверный тип аргумента. Пример: .{ctx.command} <аргументы>")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена. Используй `.help`")
    else:
        await ctx.send(f"❌ Ошибка: {error}")

# ==================== ДОХОД ПО РОЛЯМ И ПРЕДМЕТАМ ====================
@tasks.loop(minutes=1)
async def give_income():
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue

            income = 0
            # доход по ролям
            for role in member.roles:
                if role.id in role_income:
                    income += role_income[role.id].get("income", 0)

            # доход по предметам
            stats = get_user_stats(member.id)
            income += stats.get("income", 0)

            if income > 0:
                add_money(member.id, income)

bot.run(TOKEN)
