import discord
import re
from discord.ext import commands

def get_echo(echoes, echo_name):
    return echoes.find_one({"name":echo_name})

def create_echo_card(echo_name, data):
    card = discord.Embed(title = echo_name)
    image_url = data.get("image")
    if image_url:
        card.set_thumbnail(url=image_url)
    card.add_field(name="Cost", value=data["cost"])
    card.add_field(name = "出現位置", value=data["location"])
    card.add_field(name = "聲骸強度", value= data["intensity"])
    if data.get("skill"):
        description = data["skill"].get("description") or "查無技能資料"
        description = description.replace("<br>", "\n")
        description = re.sub(r"<[^>]*>", "", description)
        card.add_field(name = "聲骸描述", value=description,inline=False)
    else:
        card.add_field(name = "聲骸描述", value="查無技能資料", inline=False)

    sets = data.get("sets") or []
    set_names = []
    for set_data in sets:
        effects = set_data["effects"]
        effects_texts = []
        for effect in effects:
            effects_texts.append(f"{effect['pieces']}件套: {effect['description']}")
        effect_result = "\n".join(effects_texts)
        set_result = f"{set_data['name']}\n{effect_result}"
        set_names.append(set_result)
    result = "\n\n".join(set_names) or "查無合鳴套裝"
    card.add_field(name="合鳴套裝", value = result, inline = False)

    return card

class EchoCommands(commands.Cog):
    def __init__(self, echoes):
        self.echoes = echoes

    async def echo_autocomplete(self, interaction: discord.Interaction, current:str):
        matches = []
        for echo in self.echoes.find():
            name = echo["name"]
            if current in name:
                matches.append(name)
        return [
            discord.app_commands.Choice(name = name, value=name)
            for name in matches[:25]
        ]
    @discord.app_commands.command(
        name = "聲骸",
        description = "查詢聲骸資料"
    )
    @discord.app_commands.autocomplete(
        echo_name = echo_autocomplete
    )
    async def echo_search(self, interaction, echo_name:str):
        data = get_echo(self.echoes,echo_name)
        if data is not None:
            card = create_echo_card(echo_name, data)
            await interaction.response.send_message(embed = card)
        else:
            await interaction.response.send_message("找不到聲骸")