import discord
from discord import app_commands
from discord.ext import commands

class CharacterGuide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "角色養成攻略", description = "查詢角色養成攻略")
    @app_commands.rename(character_name = "角色")
    async def character_guide(self,interaction:discord.Interaction, character_name:str):
        await interaction.response.send_message(f"正在查詢{character_name}的角色攻略")
async def setup(bot):
    await bot.add_cog(CharacterGuide(bot))