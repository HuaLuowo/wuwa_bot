import discord
from discord.ext import commands

def get_character(characters, character_name):
    return characters.find_one({"name": character_name})

def get_attribute_color(attribute):
    if attribute == "熱熔":
        return discord.Color.red()
    elif attribute == "衍射":
        return discord.Color.yellow()
    elif attribute == "冷凝":
        return discord.Color.blue()
    elif attribute == "導電":
        return discord.Color.purple()
    elif attribute == "氣動":
        return discord.Color.green()
    elif attribute == "湮滅":
        return discord.Color.dark_purple()
    else:
        return discord.Color.orange()

def create_character_card(character_name, data):
    card_color = get_attribute_color(data["attribute"])
    card = discord.Embed(title=character_name, color=card_color)
    card.add_field(name="屬性", value=data["attribute"])
    card.add_field(name="武器", value=data["weapon"])
    card.add_field(name="稀有度", value="★" * data["rarity"])
    card.add_field(
        name="角色資料",
        value=f"生日: {data['profile']['birthday']}\n"
              f"性別: {data['profile']['sex']}\n"
              f"地區: {data['profile']['country']}\n"
              f"勢力: {data['profile']['influence']}",
              inline=False
    )
    card.set_thumbnail(url = data["image"])
    tag_names = []
    for tag in data["tags"]:
        tag_names.append(tag["name"])
    tag_text = "｜".join(tag_names)
    card.add_field(
        name = "角色定位",
        value= tag_text,
        inline=False
    )
    card.add_field(
        name= "角色介紹",
        value= data["introduction"],
        inline=False
    )

    return card

async def character_autocomplete(interaction, current, characters_list):
    result = []
    for character in characters_list.find():
        name = character["name"]
        if current in name:
            result.append(discord.app_commands.Choice(
            name= name,
            value= name
            ))
    return result[:25]  


class CharacterCommands(commands.Cog):
    def __init__(self, characters):
        self.characters = characters

    async def autocomplete_character(self, interaction, current:str):
        return await character_autocomplete(interaction,current,self.characters)

    @discord.app_commands.command(name = "角色", description="查詢角色資料")
    @discord.app_commands.autocomplete(character_name=autocomplete_character)
    async def search(self, interaction, character_name: str):
        data = get_character(self.characters, character_name)
        if data is not None:
            card = create_character_card(data["name"],data)
            await interaction.response.send_message(embed = card)
        else:
            await interaction.response.send_message("找不到角色")