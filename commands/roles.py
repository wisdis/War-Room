import discord
from discord.ext import commands
from storage import set_role_income, remove_role_income, get_all_role_income


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_role(self, ctx, action: str, role: discord.Role, income: int = 0, population: int = 0, stability: int = 0):
        action = action.lower()

        if action == "add":
            set_role_income(role.id, income, population, stability)
            await ctx.send(f"✅ Роль **{role.name}** добавлена!")
        elif action == "remove":
            remove_role_income(role.id)
            await ctx.send(f"✅ Роль **{role.name}** удалена!")
        else:
            await ctx.send("❌ Используй: add или remove")

    @commands.command(name="роли")
    async def view_roles(self, ctx):
        roles = get_all_role_income()

        if not roles:
            await ctx.send("📭 Пока нет добавленных ролей")
            return

        embed = discord.Embed(title="📋 Роли и их эффекты", color=0x00ff00)

        for role_id, d in roles.items():
            role = ctx.guild.get_role(role_id)
            name = role.name if role else f"ID {role_id}"

            embed.add_field(
                name=f"👑 {name}",
                value=f"💰 Доход: {d['income']:+d}\n👥 Население: {d['population']:+}\n🏛️ Стабильность: {d['stability']:+}",
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Roles(bot))
