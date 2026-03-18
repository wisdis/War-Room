import discord
from discord.ext import commands
import os
import random

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
    fraza = [
        "Привет!"
        "Приветствую!"
        "Добрый день 👋"
        "Здравствуйте!"
        "Салют!"
        "Хай!"
    ]
    await ctx.send(choice.random(privet))
    
bot.run(TOKEN)
