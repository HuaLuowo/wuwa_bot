import discord

def get_character(characters_list, character_name):
    if character_name in characters_list:
        return characters_list[character_name]
    else:
        return None
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
    return card

async def character_autocomplete(interaction, current, characters_list):
    result = []
    for character in characters_list:
        if current in character:
            result.append(discord.app_commands.Choice(
            name=character,
            value=character
            ))
    return result[:25]  
      