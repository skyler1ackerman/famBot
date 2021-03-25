import discord, json, asyncio
from random import choice
from discord.ext import commands
from nltk import tokenize

# Custom Errors
class NotAnAdmin(commands.CheckFailure):
	pass

def setup(bot):
	bot.add_cog(UtilBot(bot))

class UtilBot(commands.Cog):
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

	# I edited this code!
	@commands.command(name='repeat', aliases=['r'])
	async def repeat(self, ctx, rString, num):
		for x in range(int(num)):
			await ctx.send(rString)

	# @commands.command(name='google', aliases=['g'])
	# async def google(self, ctx, gString):

	@commands.command(name='joke', aliases=['j'])
	async def joke(self, ctx):
		with open('jokes.json') as json_file: 
   			randEl = choice(json.load(json_file))
   			await ctx.send(randEl['setup'])
   			await asyncio.sleep(3)
   			await ctx.send(randEl['punchline'])

	@commands.command(name='MB')
	async def moAndBo(self,ctx):
		with open('M_B.txt', 'r') as f:
   			data=tokenize.sent_tokenize(f.read())
		for line in data:
			await ctx.send(line)
			await asyncio.sleep(2)


	# Regular shut down of the bot
	@commands.command(name='s')
	@adminCheck()
	async def shutdown(self, ctx):
		await ctx.send('Shutting down Fam Bot')
		await ctx.bot.logout()