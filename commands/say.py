import discord
from discord.ext import commands
import random


class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sayto(self, ctx, channel: discord.TextChannel, *, message: str):
        await ctx.message.delete()
        await channel.send(message)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sayraw(self, ctx, *, message: str):
        await ctx.message.delete()
        color = random.randint(0, 0xFFFFFF)
        embed = discord.Embed(description=message, color=color)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def saytoraw(self, ctx, channel: discord.TextChannel, *, message: str):
        await ctx.message.delete()
        color = random.randint(0, 0xFFFFFF)
        embed = discord.Embed(description=message, color=color)
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Say(bot))
