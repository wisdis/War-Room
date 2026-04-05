from discord.ext import commands
from storage import get_shop_item_by_name, get_balance, add_money, apply_item_effects, decrease_shop_quantity

DB_PATH = "database.db"

class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def buy(self, ctx, *, item_name: str):
        item = get_shop_item_by_name(item_name)

        if not item:
            await ctx.send("❌ Предмет не найден.")
            return

        # Проверка количества
        if item["quantity"] == 0:
            await ctx.send("❌ Этот предмет закончился.")
            return

        # Проверка заблокированных ролей
        user_role_ids = [r.id for r in ctx.author.roles]

        if item["blocked_roles"]:
            for rid in item["blocked_roles"]:
                if rid in user_role_ids:
                    await ctx.send("❌ Тебе запрещено покупать этот предмет.")
                    return

        # Проверка разрешённых ролей
        if item["allowed_roles"]:
            allowed = False
            for rid in item["allowed_roles"]:
                if rid in user_role_ids:
                    allowed = True
                    break
            if not allowed:
                await ctx.send("❌ У тебя нет нужной роли для покупки этого предмета.")
                return

        # Проверка денег
        balance = get_balance(ctx.author.id)
        if balance < item["price"]:
            await ctx.send(f"❌ Не хватает денег. Нужно {item['price']}, у тебя {balance}.")
            return

        # Списываем деньги
        add_money(ctx.author.id, -item["price"])

        # Применяем эффекты + добавляем в инвентарь
        apply_item_effects(ctx.author.id, item)

        # Уменьшаем количество
        ok = decrease_shop_quantity(item["name"])
        if not ok:
            await ctx.send("❌ Ошибка: предмет закончился прямо сейчас.")
            return

        await ctx.send(f"✅ Ты купил **{item['name']}** за {item['price']} монет!")

async def setup(bot):
    await bot.add_cog(Buy(bot))
