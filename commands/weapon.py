import discord
from discord.ext import commands

def get_weapon(weapons, weapon_name):
    return weapons.find_one({"name": weapon_name})

def create_weapon_card(weapon_name, data):
    card = discord.Embed(title = weapon_name)
    card.add_field(name = "武器類型", value = data["type"])
    card.add_field(name = "星級", value = data["rarity"])
    card.add_field(name = "初始攻擊力", value = data["initial"]["attack"], inline=True)
    card.add_field(name = "滿級攻擊力", value = data["max"]["attack"])
    card.add_field(name = "副屬性", value = data["initial"]["secondary_stat"]["name"], inline=False)
    card.add_field(name = "初始副屬性數值", value=f'{data["initial"]["secondary_stat"]["value"]}%')
    card.add_field(name = "滿級副屬性數值", value =f' {data["max"]["secondary_stat"]["value"]}%')
    card.add_field(name = "武器效果", value = data["effect"]["name"], inline=False)
    card.add_field(name = "效果描述", value = data["effect"]["description"], inline=False)
    return card

class WeaponCommands(commands.Cog):
    def __init__(self, weapons):
        self.weapons = weapons
    async def weapon_autocomplete(self, interaction: discord.Interaction, current:str):
        matches = []
        for weapon in self.weapons.find():
            name = weapon["name"]
            if current in name:
                matches.append(name)
        return [
            discord.app_commands.Choice(name=name, value=name)
            for name in matches[:25]
        ]


    @discord.app_commands.command(
            name="武器",
            description="查詢武器資料"
        )
    @discord.app_commands.autocomplete(
        weapon_name = weapon_autocomplete
    )
    async def search(self, interaction, weapon_name:str):
        data = get_weapon(self.weapons, weapon_name)
        if data is not None:
            card = create_weapon_card(weapon_name,data)
            await interaction.response.send_message(embed = card)
        else:
            await interaction.response.send_massage("找不到武器")
    