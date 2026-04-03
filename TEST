# Создаем бота с префиксом "."
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')

@bot.command()
async def profile(ctx):
    user = ctx.author

    user_id = user.id
    date_discord = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    date_joined = user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else 'Нет данных'

    reply = (
        f"**Профиль пользователя:**\n"
        f"ID: {user_id}\n"
        f"Дата регистрации в Discord: {date_discord}\n"
        f"Дата присоединения к серверу: {date_joined}"
    )

    await ctx.send(reply)

git add main.py
git commit -m "Добавил бота с командой .profile"
git branch -M main
git remote add origin https://github.com/ТВОЁ_ИМЯ/имя_репозитория.git
git push -u origin main

bot.run(TOKEN)



