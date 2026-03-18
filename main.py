import discord
from discord.ext import commands

TOKEN = "твой_токен_бота"

# Intents — нужны для работы команд и событий
intents = discord.Intents.default()
intents.message_content = True  # разрешаем читать сообщения для команд

client = commands.Bot(command_prefix=".", intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.command()
async def hello(ctx):
    await ctx.send("Привет!")

client.run(TOKEN)
