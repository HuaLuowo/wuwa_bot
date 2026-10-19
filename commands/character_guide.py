import discord
from discord import app_commands
from discord.ext import commands
from character_autocomplete import character_autocomplete as shared_character_autocomplete
from commands.character import get_attribute_color


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
        return await shared_character_autocomplete(
            interaction, current, self.character_collection
        )

    @app_commands.command(name = "角色養成攻略", description = "查詢角色養成攻略")
    @app_commands.rename(character_name = "角色")
    @app_commands.autocomplete(character_name=character_autocomplete)
    async def character_guide(self,interaction:discord.Interaction, character_name:str):
        guide = get_character_guide(self.character_collection, character_name)
        if guide is None:
            await interaction.response.send_message("找不到角色攻略")
            return
        guide_url = guide.get("guide_url")

        rarity = guide.get("rarity", 0)
        stars = "★" * rarity
        tag_names = []
        for tag in guide.get("tags",[]):
            tag_names.append(tag["name"])
        tag_text = " | ".join(tag_names)

        embed = discord.Embed(
            title=f"{character_name}的角色攻略",
            description= f"{stars}\n{guide.get('attribute', '未知')} | {guide.get('weapon', '未知')}",
            color= get_attribute_color(guide.get("attribute"))
            )
        if tag_text:
            embed.add_field(
                name= "角色定位",
                value= tag_text,
                inline= False
            )
        if guide.get("character_image"):
            embed.set_image(url = guide["character_image"])
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
