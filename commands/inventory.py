import discord
from discord.ext import commands
from storage import get_user_items, get_user_stats

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inventory(self, ctx):
        items = get_user_items(ctx.author.id)
        if not items:
            await ctx.send("📦 У тебя пока нет предметов")
            return

        stats = get_user_stats(ctx.author.id)
        msg = f"📦 Твои предметы (доход: {stats['income']}, население: {stats['population']}, стабильность: {stats['stability']}):\n"

        for i, item in enumerate(items, 1):
            desc = item.get("description", "Без описания")
            buffs = ", ".join(f"{k}:+{v}" for k, v in item.get("buffs", {}).items())
            debuffs = ", ".join(f"{k}:{v}" for k, v in item.get("debuffs", {}).items())
            effects = ", ".join(filter(None, [buffs, debuffs]))
            msg += f"{i}. {item['name']} | {desc} | {effects}\n"

        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Inventory(bot))
