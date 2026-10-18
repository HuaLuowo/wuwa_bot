import discord

async def character_autocomplete(interaction, current, characters_collection):
    result = []
    for character in characters_collection.find({}, {"name":1, "_id":0}):
        name = character["name"]
        if current.lower() in name.lower():
            result.append(name)
    return[
        discord.app_commands.Choice(name = name, value= name)
        for name in result[:25]
    ]