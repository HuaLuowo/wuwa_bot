import discord
from discord import app_commands
from discord.ext import commands


def get_character_guide(character_collection, character_name):
    return character_collection.find_one({"name":character_name})

class CharacterGuide(commands.Cog):
    def __init__(self, bot,character_collection):
        self.bot = bot
        self.character_collection = character_collection

    async def character_autocomplete(
        self,
        interaction: discord.Interaction,
        current :str
    ):
        collection = self.character_collection
        characters = collection.find({}, {"name":1, "_id": 0})

        matched = []
        for character in characters:
            name = character["name"]
            if current.lower() in name.lower():
                matched.append(name)
        return[
            app_commands.Choice(name = name, value=name)
            for name in matched[:25]
        ]

    @app_commands.command(name = "角色養成攻略", description = "查詢角色養成攻略")
    @app_commands.rename(character_name = "角色")
    @app_commands.autocomplete(character_name=character_autocomplete)
    async def character_guide(self,interaction:discord.Interaction, character_name:str):
        guide = get_character_guide(self.character_collection, character_name)
        if guide is None:
            await interaction.response.send_message("找不到角色攻略")
            return
        guide_url = guide.get("guide_url")

        embed = discord.Embed(
            title=f"{character_name}的角色攻略",
            description= f"屬性:{guide.get('attribute', '未知')}"
            )
        embed.add_field(
            name = "武器類型",
            value= guide.get("weapon", "資料整理中"),
            inline=False
        )
        view = discord.ui.View()
        if guide_url:
            button = discord.ui.Button(
                label= "查看完整攻略",
                url = guide_url
            )
            view.add_item(button)
        await interaction.response.send_message(
            embed=embed,
            view= view
            )
