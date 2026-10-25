import asyncio
from discord.ext import commands
from discord import app_commands
import discord
from sonata_image import create_sonata_image

class SonataCommands(commands.Cog):
    def __init__(self, echoes_collection):
        self.echoes_collection = echoes_collection
    @app_commands.command(name = "合鳴套裝", description = "查詢合鳴套裝效果與聲骸")
    async def sonata(self, interaction: discord.Interaction, set_name: str):
        await interaction.response.defer()
        echoes = await asyncio.to_thread(
            lambda: list(self.echoes_collection.find({
                "sets.name": set_name
                }))
            )


        cost_groups = {
             4:[],
             3:[],
             1:[]
        }

        seen_names = set()
        for echo in echoes:
             name = echo.get("name")
             if name in seen_names:
                  continue
             
             cost = echo.get("cost")
             if cost in cost_groups:
                  seen_names.add(name)
                  cost_groups[cost].append(echo)
        image_buffer = await asyncio.to_thread(
             create_sonata_image,
             cost_groups
        )
        image_file = discord.File(
             image_buffer,
             filename= "sonata.png"
        )

        await interaction.followup.send(
            content=f"合鳴套裝：{set_name}\n符合的聲骸數量：{sum(len(group) for group in cost_groups.values())}",
            file= image_file
        )


    async def sonata_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ):
            set_names = await asyncio.to_thread(
                 self.echoes_collection.distinct,
                "sets.name"
                )
            return[
                 app_commands.Choice(name=name, value= name)
                 for name in set_names
                 if current.lower() in name.lower()
            ][:25]

    @sonata.autocomplete("set_name")
    async def set_name_autocomplete(
         self,
         interaction: discord.Interaction,
         current:str
    ):
         return await self.sonata_autocomplete(interaction, current)