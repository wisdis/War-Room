import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pytz

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Префикс для команд
client = commands.Bot(command_prefix=".")

# Событие при запуске бота
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Команда hello
@client.command()
async def hello(ctx):
    await ctx.send("Привет!")

# Запуск бота
client.run(TOKEN)
