import os
import pronotepy
import datetime
import discord
from discord import ui
from discord.ext import commands
from dotenv import load_dotenv

#charger le token du bot dans le fichier .env
#fichier .env doit contenir remplis correctement la ligne suivante:
#DISCORD_TOKEN=token-de-votre-bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#prefix bot avant la commande /
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=discord.Intents().all())

#donnes connection pronote
user_dict = {}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~fonction modals~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#definition du modal pour la connection a pronote
class ModalConnectPronote(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.add_item(discord.ui.InputText(label="Lien Pronote", placeholder="ex: https://demo.index-education.net/pronote/eleve.html?login=true", style=discord.InputTextStyle.paragraph))
        self.add_item(discord.ui.InputText(label="Identifiant", placeholder="ex: demonstration", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="mot de passe", placeholder="ex: pronotevs", style=discord.InputTextStyle.short))
    
    async def callback(self, interaction: discord.Interaction):
        global PronoteLink
        global Identifiant
        global Password
        global user_dict
        userid = str(interaction.user.id)  # get user id from interaction
        PronoteLink = value=self.children[0].value
        Identifiant = value=self.children[1].value
        Password = value=self.children[2].value
        user_data = {"PronoteLink": PronoteLink, "Identifiant": Identifiant, "Password": Password}
        user_dict[userid] = user_data
        client = pronotepy.Client(PronoteLink,username=Identifiant,password=Password)
        nom_utilisateur = client.info.name # get users name
        await interaction.response.send_message(f'Logged in as {nom_utilisateur}')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~commandes du bot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#exemple d'ajout d'une commande, multi-messages
#@bot.slash_command(description="Latence du botaaa")
#async def pingaaa(ctx: discord.ApplicationContext):
#    await ctx.send(f"tkt")
#    await ctx.respond(f"Ping! La latence est de {bot.latency} secondes")
            
#commande connection pronote modal
@bot.slash_command(description="Connection a Pronote")
async def pronote(ctx: discord.ApplicationContext):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = ModalConnectPronote(title="Connection a Pronote")
    await ctx.send_modal(modal)

#commande invitation du bot pronote
@bot.slash_command(description="invitation bot")
async def invite(ctx: discord.ApplicationContext):
    await ctx.respond("https://discord.com/api/oauth2/authorize?client_id=1151550156261576774&permissions=826781289472&scope=bot")
    
#commande latence du bot pronote
@bot.slash_command(description="Latence du bot")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Ping! La latence est de {bot.latency} secondes")

#commande devoirs
@bot.slash_command(description="devoirs pour aujourd'hui et apres")
async def devoirs(ctx: discord.ApplicationContext):
    userid = str(ctx.author.id)
    if userid in user_dict:
        client = pronotepy.Client(user_dict[userid]["PronoteLink"],username=user_dict[userid]["Identifiant"],password=user_dict[userid]["Password"])
        today = datetime.date.today() # store today's date using datetime built-in library
        homework = client.homework(today) # get list of homework for today and later
        nom_utilisateur = client.info.name # get users name
        await ctx.respond(f"Devoirs de {nom_utilisateur}")
        for hw in homework: # iterate through the list
            #await ctx.send(f"(Pour le {hw.date}, {hw.subject.name}): {hw.description}")
            embed=discord.Embed(title=hw.subject.name, description=hw.description, color=0x74ff38)
            embed.set_author(name="Pronote-bot", url="https://discord.com/api/oauth2/authorize?client_id=1151550156261576774&permissions=826781289472&scope=bot", icon_url="https://cdn.discordapp.com/avatars/1151550156261576774/e833dc4d36a1c97e0d991ea9240495f5.png?size=256")
            embed.set_footer(text=f"Pour le {hw.date}")
            await ctx.send(embed=embed)
    else:
        await ctx.respond(f'No user data found. Faite /pronote')
        
#commande notes
@bot.slash_command(description="liste des notes")
async def notes(ctx: discord.ApplicationContext):
    userid = str(ctx.author.id)
    if userid in user_dict:
        client = pronotepy.Client(user_dict[userid]["PronoteLink"],username=user_dict[userid]["Identifiant"],password=user_dict[userid]["Password"])
        periods = client.periods
        nom_utilisateur = client.info.name # get users name
        await ctx.respond(f"Devoirs de {nom_utilisateur}")
        for period in periods:
            for grade in period.grades:  # iterate over all the grades
                embed=discord.Embed(title=grade.subject.name, color=0x74ff38)
                embed.set_author(name="Pronote-bot", url="https://discord.com/api/oauth2/authorize?client_id=1151550156261576774&permissions=826781289472&scope=bot", icon_url="https://cdn.discordapp.com/avatars/1151550156261576774/e833dc4d36a1c97e0d991ea9240495f5.png?size=256")
                embed.add_field(name="coefficient", value=grade.coefficient, inline=True)
                embed.add_field(name="note", value=f"{grade.grade}/{grade.out_of}", inline=True)
                embed.add_field(name="moyenne", value=grade.average, inline=True)
                embed.add_field(name="commentaire", value=grade.comment, inline=False)
                embed.set_footer(text=f"Pour le {grade.date}")
                await ctx.send(embed=embed)
    else:
        await ctx.respond(f'No user data found. Faite /pronote')

#commande aide obtension du mot de passe
@bot.slash_command(description="Aide Pronote")
async def aidepronote(ctx: discord.ApplicationContext):
    await ctx.respond("https://vimeo.com/399213083")

bot.run(TOKEN)

#ajouts futur:
#-si application ne repond pas, exempel pour "/devoir" dire de se connecter a pronote