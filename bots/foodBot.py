import discord, json
from random import choice
from discord.ext import commands

# Custom Errors
class NotAnAdmin(commands.CheckFailure):
	pass

def setup(bot):
	bot.add_cog(idcwweBot(bot))

class idcwweBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot
		with open('./data/json/foodOptions.json') as f:
			self.data = json.load(f)['data']
		self.priceLabel = {0:'cheap', 1: 'pretty cheap', 2: 'a little pricy', 3: 'expensive', 4: 'expensive as fuck'}

	# Custom Error Checking
	def adminCheck():
		async def adminError(ctx):
			if not ctx.author.guild_permissions.administrator:
				raise NotAnAdmin('You are not an admin!')
			return True
		return commands.check(adminError)

	@commands.command(name='randFood', aliases=['rf'])
	async def randFood(self, ctx):
		rest = choice(self.data)
		await ctx.send('Why don\'t you try {} over at {}? It\'s {}!'.format(rest['restaurant_name'], rest['address']['street'], self.priceLabel[rest['price_range_num']]))
		if rest['cuisines'][0]:
			await ctx.send("It serves {}.".format(' and '.join(rest['cuisines'])))

	@commands.command(name='priceFood', aliases=['pf'])
	async def priceFood(self, ctx, price):
		priceList = [rest for rest in self.data if rest['price_range_num'] == int(price)]
		if not priceList:
			await ctx.send('There\'s no food with that price! Select range 0-4')
			return
		rest = choice(priceList)
		await ctx.send('Why don\'t you try {} over at {}?'.format(rest['restaurant_name'], rest['address']['street']))