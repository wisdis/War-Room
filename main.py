import discord
from discord.ext import commands
import os

# Берём токен из Environment Variable на Railway
TOKEN = os.getenv("TOKEN")

# Создаём intents
intents = discord.Intents.default()
intents.message_content = True  # важно для работы команд

# Создаём бота с префиксом "." и intents
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send("Привет!")

@bot.command()
async def help(ctx):
    help_text = """
**.hello** - бот приветствуется
**.help** - выводит список команд
"""
    # Отправляем как "кодовый блок" для форматирования
    await ctx.send(f"```{help_text}```")

bot.run(TOKEN)
