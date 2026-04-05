import discord
from discord.ext import commands
from storage import get_balance, get_user_stats, get_user_items

DB_PATH = "database.db"

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        bal = get_balance(member.id)
        stats = get_user_stats(member.id)
        items = get_user_items(member.id)

        embed = discord.Embed(title=f"👤 Профиль: {member.display_name}", color=0x00ff00)
        embed.add_field(name="💰 Баланс", value=str(bal), inline=True)
        embed.add_field(name="📈 Доход/мин", value=str(stats["income"]), inline=True)
        embed.add_field(name="👥 Население", value=str(stats["population"]), inline=True)
        embed.add_field(name="🏛️ Стабильность", value=str(stats["stability"]), inline=True)

        if items:
            text = ""
            for i, item in enumerate(items[:10], 1):
                text += f"{i}. {item['name']}\n"
            if len(items) > 10:
                text += f"...и ещё {len(items) - 10}"
            embed.add_field(name="🎒 Предметы", value=text, inline=False)
        else:
            embed.add_field(name="🎒 Предметы", value="Пусто", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def stat(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        stats = get_user_stats(member.id)

        await ctx.send(
            f"📊 Статистика {member.mention}\n"
            f"💰 Доход/мин: {stats['income']}\n"
            f"👥 Население: {stats['population']}\n"
            f"🏛️ Стабильность: {stats['stability']}"
        )


async def setup(bot):
    await bot.add_cog(Profile(bot))
