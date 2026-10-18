import discord
from discord.ext import commands
from character_autocomplete import character_autocomplete

class ChainCommands(commands.Cog):
    def __init__(self, characters):
        self.characters = characters

    async def chain_autocomplete(self, interaction, current: str):
        return await character_autocomplete(
            interaction, current, self.characters
        )

    @discord.app_commands.command(
        name = "共鳴鏈",
        description = "查詢角色共鳴鏈資訊"
    )
    @discord.app_commands.autocomplete(
        character_name = chain_autocomplete
    )
    async def search_chain(self, interaction, character_name: str):
        character = self.characters.find_one({"name": character_name})
        if character is None:
            await interaction.response.send_message("找不到角色")
            return
        chains = character["chains"]
        card = discord.Embed(
            title=f"{character['name']} - 共鳴鏈",
            color= discord.Color.blue()
        )
        for chain in chains:
            card.add_field(
                name = f"{chain['index']} - {chain['name']}",
                value= chain["description"],
                inline=False
            )
        await interaction.response.send_message(embed = card)

