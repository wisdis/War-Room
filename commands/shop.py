import discord
from discord.ext import commands
from discord.ui import View, Button
from storage import get_shop_items, get_user_items, add_money, apply_item_effects, get_balance

ITEMS_PER_PAGE = 10

class ShopView(View):
    def __init__(self, ctx, items):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.items = items
        self.page = 0
        self.max_pages = max((len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE, 1)
        self.update_buttons()

    def get_page_embed(self):
        start = self.page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = self.items[start:end]

        embed = discord.Embed(title=f"🛒 Магазин (страница {self.page + 1}/{self.max_pages})", color=0x00ff00)
        for item in page_items:
            desc = item.get("description", "Без описания")
            embed.add_field(name=f"{item['name']} | {item['price']}💰", value=desc, inline=False)
        return embed

    def update_buttons(self):
        for child in self.children:
            if isinstance(child, Button):
                if child.label == "◀ Назад":
                    child.disabled = self.page == 0
                elif child.label == "Вперёд ▶":
                    child.disabled = self.page >= self.max_pages - 1

    @discord.ui.button(label="◀ Назад", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Вперёд ▶", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if self.page < self.max_pages - 1:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx):
        items = get_shop_items()  # Корректная переменная items
        
        if not items:
            await ctx.send("🛒 Магазин пока пуст")
            return

        view = ShopView(ctx, items)
        await ctx.send(embed=view.get_page_embed(), view=view)

    @commands.command()
    async def buy(self, ctx, *, item_name):
        items = get_shop_items()  # Получаем список из базы
        item = next((i for i in items if i['name'].lower() == item_name.lower()), None)
        if not item:
            await ctx.send("❌ Такого предмета нет")
            return

        # Проверка ролей
        allowed = item.get("allowed_roles", [])
        blocked = item.get("blocked_roles", [])
        if allowed and not any(role.id in allowed for role in ctx.author.roles):
            await ctx.send("❌ Ты не можешь купить этот предмет")
            return
        if any(role.id in blocked for role in ctx.author.roles):
            await ctx.send("❌ Ты не можешь купить этот предмет")
            return

        bal = get_balance(ctx.author.id)
        if bal < item['price']:
            await ctx.send("❌ Недостаточно денег")
            return

        add_money(ctx.author.id, -item['price'])
        apply_item_effects(ctx.author.id, item)
        await ctx.send(f"✅ Ты купил **{item['name']}**!")

async def setup(bot):
    await bot.add_cog(Shop(bot))
