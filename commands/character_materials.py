import discord
from discord import app_commands
from discord.ext import commands
from character_autocomplete import character_autocomplete as shared_character_autocomplete
from material_image import create_material_image
import io
import asyncio
import traceback

class CharacterMaterials(commands.Cog):
    def __init__(self, bot, character_collection):
        self.bot = bot
        self.character_collection = character_collection

    async def character_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        return await shared_character_autocomplete(
            interaction, current, self.character_collection
        )
    @app_commands.command(name = "角色突破材料", description="查詢角色突破材料總覽")
    @app_commands.rename(character_name = "角色")
    @app_commands.autocomplete(character_name= character_autocomplete)
    async def character_materials(self, interaction: discord.Interaction, character_name:str):
        await interaction.response.defer()

        try:
            character = await asyncio.to_thread(
                self.character_collection.find_one,
                {"name": character_name}
            )
        except Exception:
            traceback.print_exc()
            await interaction.followup.send(
                "角色資料查詢失敗，請稍後再試。"
            )
            return
        if character is None:
            await interaction.followup.send("找不到角色資料")
            return
        breaches = character.get("breaches", [])
        materials_total = {}
        for breach in breaches:
            for material in breach.get("materials", []):
                name = material["material_name"]
                material_id = material["material_id"]
                quantity = material["quantity"]
                if material_id not in materials_total:
                    materials_total[material_id] = {
                        "material_id": material_id,
                        "material_name": name,
                        "quantity": 0
                    }
                materials_total[material_id]["quantity"] += quantity
        materials_list = list(materials_total.values())
        if not materials_list:
            await interaction.followup.send("這個角色沒有突破材料資料")
            return
        try:
            image = await asyncio.to_thread(
                create_material_image,
                materials_list
            )
            image_buffer = io.BytesIO()
            image.save(image_buffer, format="PNG")
            image_buffer.seek(0)
            file = discord.File(image_buffer, filename="character_materials.png")
        except Exception:
            traceback.print_exc()
            await interaction.followup.send(
                "材料圖片產生失敗，請稍後再試。"
            )
            return
        try:
            await interaction.followup.send(
                content= f"{character_name} 突破材料總覽",
                file= file
            )
        except discord.HTTPException:
            traceback.print_exc()
            try:
                await interaction.followup.send(
                    "圖片傳送失敗，請稍後再試。"
                )
            except discord.HTTPException:
                traceback.print_exc()