import discord
# # You can replace this with your own token in the config file
from config import TOKEN
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

extensions = ['raidBot', 'foodBot', 'leagueBot', 'utilBot', 'secretBot', 'imgBot', 'helpBot']

for exten in extensions:
	bot.load_extension('bots.{}'.format(exten))

@bot.event
async def on_ready():
	print("Fam Bot is online.")
	await bot.change_presence(status=discord.Status.online, activity=discord.Game('Hanging out'))

bot.run(TOKEN)