import discord, json, asyncio, datetime
import unicodedata
from random import choice
from discord.ext import commands
from nltk import tokenize

# Custom Errors
class NotAnAdmin(commands.CheckFailure):
	pass

class NotOwner(commands.CheckFailure):
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

	def meCheck():
		async def meErr(ctx):
			if ctx.author.name != 'thomasm16' or ctx.author.discriminator != '5700':
				await ctx.send('Sorry, that\'s for thomasm16 only')
				raise NotOwner('You are not the owner!')
			return True
		return commands.check(meErr)

	# I edited this code!
	@commands.command(name='repeat', aliases=['r'])
	async def repeat(self, ctx, rString, num):
		for x in range(int(num)):
			await ctx.send(rString)

	# @commands.command(name='google', aliases=['g'])
	# async def google(self, ctx, gString):

	@commands.command(name='joke', aliases=['j'])
	async def joke(self, ctx):
		with open('jokes.json') as jokes_file: 
   			randEl = choice(json.load(jokes_file))
   			await ctx.send(randEl['setup'])
   			await asyncio.sleep(3)
   			await ctx.send(randEl['punchline'])


	@commands.command(name='quote', aliases=['q'])
	async def quote(self, ctx):
		with open('quotes.json') as quotes_file:
			randEl = choice(json.load(quotes_file))
			await ctx.send('{} - {}'.format(randEl['text'], randEl['author']))

	@commands.command(name='MB')
	async def moAndBo(self,ctx):
		with open('M_B.txt', 'r') as f:
   			data=tokenize.sent_tokenize(f.read())
		for line in data:
			await ctx.send(line)
			await asyncio.sleep(2)

	@commands.command(name='owner')
	async def owner(self, ctx):
		await ctx.send('{} owns this server.'.format(ctx.guild.owner.nick))

	@commands.command(name='loveme')
	async def loveme(self, ctx):
		loveList = ['I love you {}', 'Please {}, have my kids', 'There\'s no one I love more than {}']
		await ctx.send(choice(loveList).format(ctx.author.mention))

	@commands.command(name='imageTester', aliases=['it'])
	@meCheck()
	async def imageTester(self, ctx):
		image_types = ["png", "jpeg", "gif", "jpg"]
		for attach in ctx.message.attachments:
			if any(attach.filename.lower().endswith(image) for image in image_types) and not ctx.message.author.bot:
				await attach.save('./data/' + attach.filename)
				await ctx.send(file=discord.File(attach.filename))

	def transform(self, message):
		return "{} ({}): {}".format(message.created_at.strftime("[%m/%d/%y] %I:%M %p %Z"), message.author.name, message.content)

	# TODO: Fix this
	@commands.command(name='hist')
	@meCheck()
	async def history(self, ctx):
		allHist = await ctx.channel.history(limit=None).map(self.transform).flatten()
		with open(filename:='./data/' + ctx.channel.name + '_log.txt', 'w') as f:
			for m in [elm for elm in reversed(allHist)]:
				try:
					f.write('%s\n' % m)
				except:
					f.write('ERROR\n')
		await ctx.send(file=discord.File(filename))


	@commands.command(name='ree')
	async def reactSpeller(self, ctx, eString):
		# TODO: Check for duplicates
		hist = await ctx.channel.history(limit=2).flatten()
		await ctx.message.delete()
		for c in eString.lower():
			await hist[1].add_reaction(chr(ord(c)+127365))

	@commands.command(name='info')
	async def info(self, ctx):
		await ctx.send('This is {}, owned by {}.\n It has {} voice channels, {} text channels, and premium tier {}.'\
			.format(ctx.guild.name, ctx.guild.owner.nick, len(ctx.guild.voice_channels), len(ctx.guild.text_channels), ctx.guild.premium_tier))


	# Regular shut down of the bot
	@commands.command(name='s')
	@adminCheck()
	async def shutdown(self, ctx):
		await ctx.send('Shutting down Fam Bot')
		await ctx.bot.logout()