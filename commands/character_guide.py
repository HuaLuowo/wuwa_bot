import discord
from discord import app_commands
from discord.ext import commands

def get_character_guide(character_guides, character_name):
    return character_guides.find_one({"name":character_name})

class CharacterGuide(commands.Cog):
    def __init__(self, bot,character_guides):
        self.bot = bot
        self.character_guides = character_guides

    @app_commands.command(name = "角色養成攻略", description = "查詢角色養成攻略")
    @app_commands.rename(character_name = "角色")
    async def character_guide(self,interaction:discord.Interaction, character_name:str):
        guide = get_character_guide(self.character_guides, character_name)
        if guide is None:
            await interaction.response.send_message("找不到角色攻略")
            return

        embed = discord.Embed(
            title=f"{character_name}的角色攻略",
            description= "正在整理中"
            )
        embed.add_field(
            name = "推薦武器",
            value= guide.get("weapon", "資料整理中"),
            inline=False
        )
        embed.add_field(
            name="推薦聲骸",
            value= guide.get("echo", "資料整理中"),
            inline=False
        )
        embed.add_field(
                    name="技能升級順序",
                    value= guide.get("skill", "資料整理中"),
                    inline=False
                )
        await interaction.response.send_message(embed=embed)
