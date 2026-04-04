import sqlite3
from discord.ext import commands
import discord
import json
from storage import add_shop_item  # функция для добавления предмета в базу

DB_PATH = "database.db"  # путь к базе

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
        result = []
        for i in items:
            result.append({
                "name": i[0],
                "price": i[1],
                "description": i[2],
                "buffs": json.loads(i[3]) if i[3] else {},
                "debuffs": json.loads(i[4]) if i[4] else {},
                "allowed_roles": json.loads(i[5]) if i[5] else [],
                "blocked_roles": json.loads(i[6]) if i[6] else [],
                "quantity": i[7] or -1
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

    # ===== Команда: добавить предмет (пошагово) =====
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_item(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # 1. Название
        await ctx.send("Введите название предмета:")
        msg = await self.bot.wait_for("message", check=check)
        name = msg.content

        # 2. Цена
        await ctx.send(f"Введите цену для {name}:")
        msg = await self.bot.wait_for("message", check=check)
        try:
            price = int(msg.content)
        except:
            await ctx.send("Неверное число. Отмена.")
            return

        # 3. Описание
        await ctx.send(f"Введите описание для {name}:")
        msg = await self.bot.wait_for("message", check=check)
        description = msg.content

        # 4. Баффы
        await ctx.send("Введите баффы через запятую, например: attack+10, defense-5, income+20, stability+5, population+2\nЕсли нет — напишите none:")
        msg = await self.bot.wait_for("message", check=check)
        buffs = {}
        if msg.content.lower() != "none":
            for part in msg.content.split(","):
                part = part.strip()
                if "+" in part:
                    key, val = part.split("+")
                    buffs[key.strip()] = int(val.strip())
                elif "-" in part:
                    key, val = part.split("-")
                    buffs[key.strip()] = -int(val.strip())

        # 5. Количество
        await ctx.send(f"Введите количество для {name} (напишите 'none' для бесконечного запаса):")
        msg = await self.bot.wait_for("message", check=check)
        if msg.content.lower() == "none":
            quantity = -1
        else:
            try:
                quantity = int(msg.content)
            except:
                quantity = 1

        # 6. Разрешённые роли
        await ctx.send("Введите теги разрешённых ролей через пробел, например: @Государство @everyone\nЕсли нет — напишите none:")
        msg = await self.bot.wait_for("message", check=check)
        allowed_roles = [role.id for role in msg.role_mentions] if msg.content.lower() != "none" else []

        # 7. Заблокированные роли
        await ctx.send("Введите теги заблокированных ролей через пробел, например: @Бандиты\nЕсли нет — напишите none:")
        msg = await self.bot.wait_for("message", check=check)
        blocked_roles = [role.id for role in msg.role_mentions] if msg.content.lower() != "none" else []

        # Создаём объект предмета
        item = {
            "name": name,
            "price": price,
            "description": description,
            "buffs": buffs,
            "debuffs": {},
            "allowed_roles": allowed_roles,
            "blocked_roles": blocked_roles,
            "quantity": quantity
        }

        # Добавляем в базу через функцию
        add_shop_item(item)
        await ctx.send(f"✅ Предмет **{name}** добавлен в магазин!")

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
        embed.add_field(name="Количество", value=str(item["quantity"]) if item["quantity"] != -1 else "∞")
        embed.add_field(name="Баффы", value=str(item["buffs"]) or "нет", inline=False)
        embed.add_field(name="Дебаффы", value=str(item["debuffs"]) or "нет", inline=False)
        embed.add_field(name="Разрешённые роли", value=", ".join(str(r) for r in item["allowed_roles"]) or "нет", inline=False)
        embed.add_field(name="Заблокированные роли", value=", ".join(str(r) for r in item["blocked_roles"]) or "нет", inline=False)

        await ctx.send(embed=embed)

    # ===== Команда: редактировать предмет =====
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def edit_item(self, ctx, name: str, field: str, *, new_value):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name, price, description, buffs, debuffs, allowed_roles, blocked_roles, quantity FROM shop WHERE LOWER(name)=?", (name.lower(),))
        row = cur.fetchone()
        if not row:
            await ctx.send("❌ Предмет не найден")
            conn.close()
            return

        item = {
            "name": row[0],
            "price": row[1],
            "description": row[2],
            "buffs": json.loads(row[3]) if row[3] else {},
            "debuffs": json.loads(row[4]) if row[4] else {},
            "allowed_roles": json.loads(row[5]) if row[5] else [],
            "blocked_roles": json.loads(row[6]) if row[6] else [],
            "quantity": row[7] or -1
        }

        field = field.lower()
        if field == "name":
            item["name"] = new_value
        elif field == "price":
            try:
                item["price"] = int(new_value)
            except:
                await ctx.send("❌ Цена должна быть числом")
                conn.close()
                return
        elif field == "description":
            item["description"] = new_value
        elif field == "buffs":
            buffs = {}
            if new_value.lower() != "none":
                for part in new_value.split(","):
                    part = part.strip()
                    if "+" in part:
                        key, val = part.split("+")
                        buffs[key.strip()] = int(val.strip())
                    elif "-" in part:
                        key, val = part.split("-")
                        buffs[key.strip()] = -int(val.strip())
            item["buffs"] = buffs
        elif field == "quantity":
            if new_value.lower() == "none":
                item["quantity"] = -1
            else:
                try:
                    item["quantity"] = int(new_value)
                except:
                    await ctx.send("❌ Количество должно быть числом")
                    conn.close()
                    return
        elif field == "allowed_roles":
            item["allowed_roles"] = [role.id for role in ctx.message.role_mentions] if new_value.lower() != "none" else []
        elif field == "blocked_roles":
            item["blocked_roles"] = [role.id for role in ctx.message.role_mentions] if new_value.lower() != "none" else []
        else:
            await ctx.send("❌ Неверное поле. Доступные: name, price, description, buffs, quantity, allowed_roles, blocked_roles")
            conn.close()
            return

        cur.execute("""
        UPDATE shop
        SET name=?, price=?, description=?, buffs=?, debuffs=?, allowed_roles=?, blocked_roles=?, quantity=?
        WHERE LOWER(name)=?
        """, (
            item["name"], item["price"], item["description"], json.dumps(item["buffs"]),
            json.dumps(item["debuffs"]), json.dumps(item["allowed_roles"]),
            json.dumps(item["blocked_roles"]), item["quantity"], name.lower()
        ))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Предмет **{item['name']}** обновлён. Поле {field} изменено.")

# ===== Регистрация COG =====
async def setup(bot):
    await bot.add_cog(Shop(bot))
