import discord
from discord.ext import commands
import os
import random
import asyncio
from discord.ui import View

# ==========================
# DATABASE (встроено в main.py)
# ==========================

shop_items = []
user_items = {}
user_balance = {}
user_stats = {}

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


# ==========================
# DISCORD BOT
# ==========================

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

role_income = {}

ITEMS_PER_PAGE = 10


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе")
    bot.loop.create_task(give_income())


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Ошибка: пропущен аргумент.\nПример: .{ctx.command} <аргументы>")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Ошибка: неверный тип аргумента.\nПример: .{ctx.command} <аргументы>")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена. Используй `.help` чтобы увидеть все команды")
    else:
        await ctx.send(f"❌ Произошла ошибка: {str(error)}")


async def give_income():
    while True:
        for guild in bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                income = 0

                for role in member.roles:
                    if role.id in role_income:
                        income += role_income[role.id].get("income", 0)

                stats = get_user_stats(member.id)
                income += stats.get("income", 0)

                if income > 0:
                    add_money(member.id, income)

        await asyncio.sleep(60)


@bot.command()
async def привет(ctx):
    ответы = [
        "Привет! 👋",
        "Приветствую! ✨",
        "Добрый день 👋",
        "Здравствуйте! 🌟",
        "Салют! 🔥",
        "Хай! 🚀"
    ]
    await ctx.send(random.choice(ответы))


@bot.command()
async def balance(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"💰 Твой баланс: **{bal}** монет")


@bot.command()
async def bal(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"💰 Твой баланс: **{bal}** монет")


@bot.command()
@commands.has_permissions(administrator=True)
async def give(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Сумма должна быть больше 0")
        return

    add_money(member.id, amount)
    await ctx.send(f"✅ Выдал {amount} монет пользователю {member.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def take(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Сумма должна быть больше 0")
        return

    add_money(member.id, -amount)
    await ctx.send(f"✅ Забрал {amount} монет у {member.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def add_item(ctx):
    await ctx.send("Название предмета?")
    name = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Цена?")
    price = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    try:
        price_value = int(price.content)
    except:
        await ctx.send("❌ Введите число")
        return

    await ctx.send("Описание (или 'skip')")
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

    shop_items.append(item)
    await ctx.send(f"✅ Предмет **{item['name']}** успешно создан!")


def can_buy(member, item):
    if item["allowed_roles"]:
        if not any(role.id in item["allowed_roles"] for role in member.roles):
            return False

    if any(role.id in item["blocked_roles"] for role in member.roles):
        return False

    return True


@bot.command()
async def buy(ctx, *, item_name):
    item = next((i for i in shop_items if i["name"].lower() == item_name.lower()), None)

    if not item:
        await ctx.send("❌ Такого предмета нет в магазине")
        return

    if not can_buy(ctx.author, item):
        await ctx.send("❌ Ты не можешь купить этот предмет")
        return

    balance = get_balance(ctx.author.id)
    if balance < item["price"]:
        await ctx.send("❌ У тебя недостаточно денег 💰")
        return

    add_money(ctx.author.id, -item["price"])
    apply_item_effects(ctx.author.id, item)

    await ctx.send(f"✅ Ты купил **{item['name']}**!")


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_role(ctx, action: str, role: discord.Role, income: int = 0, population: int = 0, stability: int = 0):
    action = action.lower()

    if action == "add":
        role_income[role.id] = {
            "income": income,
            "population": population,
            "stability": stability
        }
        await ctx.send(f"✅ Роль **{role.name}** добавлена с эффектами!")

    elif action == "remove":
        if role.id in role_income:
            del role_income[role.id]
            await ctx.send(f"✅ Роль **{role.name}** удалена")
        else:
            await ctx.send("❌ Роль не найдена")


@bot.command(name="роли")
async def view_roles(ctx):
    if not role_income:
        await ctx.send("📭 Пока нет добавленных ролей с эффектами")
        return

    embed = discord.Embed(title="📋 Добавленные роли и их эффекты", color=0x00ff00)

    for role_id, data in role_income.items():
        role = ctx.guild.get_role(role_id)
        role_name = role.name if role else f"Неизвестная роль (ID: {role_id})"

        income = data.get("income", 0)
        population = data.get("population", 0)
        stability = data.get("stability", 0)

        embed.add_field(
            name=f"👑 {role_name}",
            value=(
                f"💰 Доход: {income:+} в минуту\n"
                f"👥 Население: {population:+}\n"
                f"🏛️ Стабильность: {stability:+}"
            ),
            inline=False
        )

    await ctx.send(embed=embed)


class ShopView(View):
    def __init__(self, ctx, items):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.items = items
        self.page = 0
        self.message = None
        self.max_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if items else 1
        self.update_buttons()

    def get_page_embed(self):
        start = self.page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = self.items[start:end]

        embed = discord.Embed(
            title=f"🛒 Магазин (страница {self.page + 1}/{self.max_pages})",
            color=0x00ff00
        )

        for item in page_items:
            desc = item["description"] if item["description"] else "Без описания"
            embed.add_field(
                name=f"{item['name']} | {item['price']}💰",
                value=desc,
                inline=False
            )

        return embed

    def update_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.label == "◀ Назад":
                    child.disabled = (self.page == 0)
                elif child.label == "Вперёд ▶":
                    child.disabled = (self.page >= self.max_pages - 1)

    @discord.ui.button(label="◀ Назад", style=discord.ButtonStyle.primary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Вперёд ▶", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_pages - 1:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    async def send_initial(self):
        self.message = await self.ctx.send(embed=self.get_page_embed(), view=self)


@bot.command()
async def shop(ctx):
    if not shop_items:
        await ctx.send("🛒 Магазин пока пуст")
        return

    view = ShopView(ctx, shop_items)
    await view.send_initial()


bot.run(TOKEN)
