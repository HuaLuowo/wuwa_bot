import discord
from discord import app_commands
from discord.ext import commands
from character_autocomplete import character_autocomplete as shared_character_autocomplete
from commands.character import get_attribute_color


def get_character_guide(character_collection, character_name):
    return character_collection.find_one({"name":character_name})

class CharacterGuideView(discord.ui.View):
    def __init__(self,guide):
        super().__init__(timeout=180)
        self.guide = guide
        self.page = 0

    @discord.ui.button(label="上一頁", style=discord.ButtonStyle.primary)
    async def previous_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
        ):
        if self.page >0:
            self.page -= 1
        await interaction.response.edit_message(
            embed= self.create_embed(),
            view= self
        )

    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.primary)
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.page < 3:
            self.page += 1
        await interaction.response.edit_message(
            embed= self.create_embed(),
            view= self
        )


    def create_embed(self):
        rarity = self.guide.get("rarity", 0)
        stars = "★" * rarity
        attribute = self.guide.get("attribute", "未知")
        weapon = self.guide.get("weapon", "未知")
        embed = discord.Embed(
            title= self.guide["name"],
            description=f"第{self.page+1}頁\n{stars}\n{attribute} | {weapon}" if self.page == 0 else 
            f"第{self.page+1}頁",
            color= get_attribute_color(attribute)
        )
        tag_names = []
        for tag in self.guide.get("tags", []):
            tag_names.append(tag["name"])
        tag_text = " | ".join(tag_names)
        if self.page == 0 and tag_text:
            embed.add_field(
                name = "角色定位",
                value= tag_text,
                inline=False
            )
        if self.page == 0 and self.guide.get("character_image"):
            embed.set_image(url = self.guide["character_image"])
        if self.page == 1:
            skills = self.guide.get("skills", [])
            for skill in skills:
                embed.add_field(
                    name= skill["type"],
                    value= skill["name"],
                    inline=False
                )
        if self.page == 2:
            chains = self.guide.get("chains", [])
            for chain in chains:
                embed.add_field(
                    name = chain.get("name", "未知共鳴鏈"),
                    value= chain.get("description") or "暫無說明",
                    inline= False
                )
        if self.page == 3:
            breaches = self.guide.get("breaches", [])
            for breach in breaches:
                material_text = []
                for material in breach.get("materials", []):
                    material_text.append(
                        f"{material['material_name']} × {material['quantity']}"
                    )

                embed.add_field(
                    name = f"突破階段 {breach['level']}",
                    value= "\n".join(material_text) or "暫無資料",
                    inline=False
                )
        return embed

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

        view = CharacterGuideView(guide)
        if guide_url:
            button = discord.ui.Button(
                label= "查看完整攻略",
                url = guide_url
            )
            view.add_item(button)
        await interaction.response.send_message(
            embed=view.create_embed(),
            view= view
            )
