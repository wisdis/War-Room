import discord
from discord.ext import commands
import os
import random
import asyncio
from database import add_money, get_user_items, shop, get_balance, apply_item_effects
from discord.ui import View

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

                items = get_user_items(member.id) or []
                for item in items:
                    if isinstance(item, dict):
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
        await ctx.send("❌ Введите число")
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
    item = next((i for i in shop if i["name"].lower() == item_name.lower()), None)
    if not item:
        await ctx.send("❌ Такого предмета нет в магазине")
        return

    if not can_buy(ctx.author, item):
        await ctx.send("❌ Вы не можете купить этот предмет")
        return

    balance = get_balance(ctx.author.id)
    if balance < item["price"]:
        await ctx.send("❌ У вас недостаточно денег 💰")
        return

    add_money(ctx.author.id, -item["price"])
    apply_item_effects(ctx.author.id, item)

    await ctx.send(f"✅ Вы успешно купили **{item['name']}**!")

@bot.command()
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

# ==================== НОВАЯ КОМАНДА .роли ====================
@bot.command(name="роли")
async def view_roles(ctx):
    """Просмотр всех добавленных ролей + их баффы/дебаффы"""
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
                f"💰 **Доход:** {income:+} в минуту\n"
                f"👥 **Население:** {population:+}\n"
                f"🏛️ **Стабильность:** {stability:+}"
            ),
            inline=False
        )
    await ctx.send(embed=embed)

ITEMS_PER_PAGE = 10

class ShopView(View):
    def __init__(self, ctx, items):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.items = items
        self.page = 0
        self.message = None
        self.max_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if items else 0
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
            desc = item['description'] if item['description'] else "Без описания"
            embed.add_field(
                name=f"{item['name']} | {item['price']}💰",
                value=desc,
                inline=False
            )
        return embed

    def update_buttons(self):
        """Отключаем кнопки, когда нельзя листать"""
        for item in self.children:
            if item.label == "◀ Назад":
                item.disabled = (self.page == 0)
            elif item.label == "Вперёд ▶":
                item.disabled = (self.page >= self.max_pages - 1)

    @discord.ui.button(label="◀ Назад", style=discord.ButtonStyle.primary)
    async def prev(self, interaction):
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            embed = self.get_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Вперёд ▶", style=discord.ButtonStyle.primary)
    async def next(self, interaction):
        if self.page < self.max_pages - 1:
            self.page += 1
            self.update_buttons()
            embed = self.get_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    async def send_initial(self):
        embed = self.get_page_embed()
        self.message = await self.ctx.send(embed=embed, view=self)


@bot.command()
async def shop(ctx):
    if not shop:
        await ctx.send("🛒 Магазин пока пуст")
        return

    view = ShopView(ctx, shop)
    await view.send_initial()

bot.run(TOKEN)
