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
        else:
            await ctx.send("❌ Действие должно быть `add` или `remove`")

    @commands.command(name="роли")
    async def view_roles(self, ctx):
        role_income = get_all_role_income()

        if not role_income:
            await ctx.send("📭 Пока нет добавленных ролей с эффектами")
            return

        embed = discord.Embed(title="📋 Роли и их эффекты", color=0x00ff00)
        for role_id, data in role_income.items():
            role = ctx.guild.get_role(role_id)
            role_name = role.name if role else f"Неизвестная роль (ID: {role_id})"
            income = data.get("income", 0)
            population = data.get("population", 0)
            stability = data.get("stability", 0)
            embed.add_field(
                name=f"👑 {role_name}",
                value=f"💰 Доход: {income:+} в минуту\n👥 Население: {population:+}\n🏛️ Стабильность: {stability:+}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Roles(bot))
