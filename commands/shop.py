import sqlite3
from discord.ext import commands
import discord

DB_PATH = "database.db"  # путь к твоей базе

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ===== Получение всех предметов =====
    def get_shop_items(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, description, buffs, debuffs, allowed_roles, blocked_roles, quantity FROM shop")
        items = cursor.fetchall()
        conn.close()
        # Преобразуем в список словарей
        result = []
        for i in items:
            result.append({
                "name": i[0],
                "price": i[1],
                "description": i[2],
                "buffs": eval(i[3]) if i[3] else {},
                "debuffs": eval(i[4]) if i[4] else {},
                "allowed_roles": eval(i[5]) if i[5] else [],
                "blocked_roles": eval(i[6]) if i[6] else [],
                "quantity": i[7] or 1
            })
        return result

    # ===== Команда: показать магазин =====
    @commands.command()
    async def shop(self, ctx):
        items = self.get_shop_items()
        if not items:
            await ctx.send("Магазин пуст")
            return
        msg = "\n".join([f"{i['name']} — {i['price']} монет" for i in items])
        await ctx.send(msg)

    # ===== Команда: добавить предмет =====
    @commands.command()
    async def add_item(self, ctx, name, price: int, description, *, effects):
        # Разбор эффектов: attack+10, defense-5, income+20, stability+5, population-2
        buffs = {}
        debuffs = {}
        allowed_roles = []
        blocked_roles = []
        quantity = 1

        for part in effects.split(","):
            part = part.strip()
            if part.startswith("attack+") or part.startswith("defense+") or part.startswith("income+") or part.startswith("stability+") or part.startswith("population+"):
                key, val = part.split("+")
                buffs[key] = int(val)
            elif part.startswith("attack-") or part.startswith("defense-") or part.startswith("income-") or part.startswith("stability-") or part.startswith("population-"):
                key, val = part.split("-")
                debuffs[key] = int(val)
            elif part.startswith("allowed_roles:"):
                allowed_roles = [int(x) for x in part.replace("allowed_roles:", "").split(";")]
            elif part.startswith("blocked_roles:"):
                blocked_roles = [int(x) for x in part.replace("blocked_roles:", "").split(";")]
            elif part.startswith("quantity:"):
                quantity = int(part.replace("quantity:", ""))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO shop (name, price, description, buffs, debuffs, allowed_roles, blocked_roles, quantity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, price, description, str(buffs), str(debuffs), str(allowed_roles), str(blocked_roles), quantity))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Предмет **{name}** добавлен в магазин")

    # ===== Команда: удалить предмет =====
    @commands.command()
    async def remove_item(self, ctx, *, name):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shop WHERE LOWER(name)=?", (name.lower(),))
        conn.commit()
        conn.close()
        await ctx.send(f"🗑️ Предмет **{name}** удалён из магазина")

    # ===== Команда: информация о предмете =====
    @commands.command()
    async def item_info(self, ctx, *, name):
        items = self.get_shop_items()
        item = next((i for i in items if i["name"].lower() == name.lower()), None)
        if not item:
            await ctx.send("❌ Предмет не найден")
            return

        embed = discord.Embed(title=f"Информация о {item['name']}", color=0x00ff00)
        embed.add_field(name="Цена", value=str(item["price"]))
        embed.add_field(name="Описание", value=item["description"] or "Отсутствует", inline=False)
        embed.add_field(name="Количество", value=str(item["quantity"]))
        embed.add_field(name="Баффы", value=str(item["buffs"]) or "нет", inline=False)
        embed.add_field(name="Дебаффы", value=str(item["debuffs"]) or "нет", inline=False)
        embed.add_field(name="Разрешённые роли", value=", ".join(str(r) for r in item["allowed_roles"]) or "нет", inline=False)
        embed.add_field(name="Заблокированные роли", value=", ".join(str(r) for r in item["blocked_roles"]) or "нет", inline=False)

        await ctx.send(embed=embed)

# ===== Регистрация COG =====
def setup(bot):
    bot.add_cog(Shop(bot))
