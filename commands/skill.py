import discord
from discord.ext import commands
from commands.character import character_autocomplete

class SkillSelect(discord.ui.Select):
    def __init__(self,skills):
        self.skills = skills

        options = []
        for index,skill in enumerate(skills):
            skill_name = skill["name"] or "未命名技能"

            options.append(
                discord.SelectOption(
                    label= skill_name,
                    value= str(index)
                )
            )

        super().__init__(
            placeholder = "選擇要查看的技能",
            options = options
        )
    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        skill = self.skills[selected_index]
        skill_name = skill["name"] or "未命名技能"
        card = discord.Embed(
            title= skill_name,
            description= skill["description"],
            color= discord.Color.blue()
        )

        await interaction.response.send_message(
            embed= card,
            ephemeral= True
        )

class SkillView(discord.ui.View):
    def __init__(self,skills):
        super().__init__(timeout = 180)
        self.add_item(SkillSelect(skills))

class SkillCommands(commands.Cog):
    def __init__(self,characters):
        self.characters = characters
    async def autocomplete_character(self,interaction, current:str):
        return await character_autocomplete(
            interaction, current, self.characters
        )
    @discord.app_commands.command(
        name= "技能",
        description="查詢技能資料"
    )
    @discord.app_commands.autocomplete(
        character_name = autocomplete_character
    )
    async def search_skill(self,interaction, character_name: str):
        character = self.characters.find_one({"name": character_name})
        if character is None:
            await interaction.response.send_message("找不到角色")
            return
        skills = character["skills"]
        card = discord.Embed(
            title= f"{character['name']} -技能資料",
            color= discord.Color.blue()
        )
        for skill in skills:
            skill_name = skill["name"]
            if not skill_name:
                skill_name = "未命名技能"
                
            card.add_field(
                name = skill_name,
                value = skill["type"],
                inline = False
        )
        await interaction.response.send_message(
            embed = card,
            view = SkillView(skills)
        )
