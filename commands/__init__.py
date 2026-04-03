from .economy import Economy
from .inventory import Inventory
from .shop import Shop
from .roles import Roles

def setup(bot):
    bot.add_cog(Economy(bot))
    bot.add_cog(Inventory(bot))
    bot.add_cog(Shop(bot))
    bot.add_cog(Roles(bot))
