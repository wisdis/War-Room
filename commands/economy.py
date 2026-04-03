import discord
from discord.ext import commands
from storage import get_balance, add_money, get_user_items
from utils import can_buy, apply_item_effects_to_user

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx):
        bal = get_balance(ctx.author.id)
        await ctx.send(f"💰 Твой баланс: **{bal}** монет")

    @commands.command()
    async def bal(self, ctx):
        bal = get_balance(ctx.author.id)
        await ctx.send(f"💰 Твой баланс: **{bal}** монет")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("❌ Сумма должна быть больше 0")
            return
        add_money(member.id, amount)
        await ctx.send(f"✅ Выдал {amount} монет пользователю {member.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def take(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("❌ Сумма должна быть больше 0")
            return
        add_money(member.id, -amount)
        await ctx.send(f"Забрал {amount} монет у пользователя {member.mention}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
