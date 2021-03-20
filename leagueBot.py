import discord, json, asyncio
import requests, requests, urllib.parse, json
from bs4 import BeautifulSoup
from discord.ext import commands

# Custom Errors
class NotAnAdmin(commands.CheckFailure):
	pass

def setup(bot):
	bot.add_cog(LeagueBot(bot))

class LeagueBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot

	# Custom Error Checking
	def adminCheck():
		async def adminError(ctx):
			if not ctx.author.guild_permissions.administrator:
				raise NotAnAdmin('You are not an admin!')
			return True
		return commands.check(adminError)

	def getCountersDict(self, champ):
		# Create the url using the champ inputed
		URL = 'https://na.op.gg/champion/' + champ.lower()
		# Get the page and soup object
		page = requests.get(URL, allow_redirects=True)
		# Have to do this to get to default page
		page = requests.get(page.url + '/matchup')
		soup = BeautifulSoup(page.content, features="html.parser")
		# Get all the counter data
		champDict = {}
		for champ in soup.find_all(class_='champion-matchup-champion-list__item'):
			champDict[champ['data-champion-name'].capitalize()] = float(champ['data-value-winrate'])
		# Return sorted data
		return {k: v for k, v in sorted(champDict.items(), key=lambda item: item[1])}

	@commands.command(name='countersChamp', aliases=['cch'])
	async def countersChamp(self, ctx, champ, num=3):
		countersDict = self.getCountersDict(champ)
		for key, val in list(countersDict.items())[:int(num)]:
			await ctx.send(champ.lower().capitalize() + ' has a ' + "{0:.2f}%".format(val*100) + ' winrate vs ' + key)


	@commands.command(name='champCounters', aliases=['chc'])
	async def champCounters(self, ctx, champ, num=3):
		countersDict = self.getCountersDict(champ)
		for key, val in list(countersDict.items())[-int(num):]:
			await ctx.send(champ.lower().capitalize() + ' has a ' + "{0:.2f}%".format(val*100) + ' winrate vs ' + key)