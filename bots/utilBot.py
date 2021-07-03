import asyncio, datetime, unicodedata, re, secrets # , ffmpeg, youtube_dl
from dateutil.parser import parse
from random import choice
from nltk import tokenize
from .common import *
from random import choice

me = discord.Client()

def setup(bot):
	bot.add_cog(UtilBot(bot))

# TODO: Cogs inheritance?
class UtilBot(commands.Cog, description='General Utility Functions'):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot

	@commands.command(name='alarm', help="""Sets a timer for a given datetime.
		\nJust put the datetime anywhere in the string in pretty much any format""")
	async def alarm(self, ctx, *, message):
		datetime, message = parse(message, fuzzy_with_tokens = True)
		message = re.sub(' +', ' ', " ".join(message))
		await asyncio.sleep((datetime - datetime.now()).total_seconds())
		await ctx.send(f'{ctx.author.mention} - {message}')

	@commands.command(name='timer', help='Sets a timer after a certain number of minutes.\nUse with !timer <minutes> <message>')
	async def timer(self, ctx, minutes:int, *, message):
		await asyncio.sleep(minutes*60)
		await ctx.send(f'{ctx.author.mention} - {message}')

	@commands.command(name='coinToss', aliases=['ct'], help='Flips a coin!')
	async def coinToss(self, ctx):
		opList = ['Heads!', 'Tails!']
		await ctx.send(choice(opList))

	@commands.command(name='requestRole', aliases=['rr'], brief='Requests a role', \
		help='Requests a role by sending a dm to the guild owner.')
	async def requestRole(self, ctx, role:discord.Role):
		await ctx.send('Requesting role, standby')
		await ctx.guild.owner.create_dm()
		reqMsg = await ctx.guild.owner.dm_channel.send("""User {0.author.name} is requesting the {1} role '+ 
			in the {0.guild.name} server""".format(ctx, role.name))
		await reqMsg.add_reaction('✅')
		await reqMsg.add_reaction('❌')

		async def giveRole(ctx):
			await ctx.author.add_roles(role)
			await ctx.send(f'Request approved by {ctx.guild.owner.name}')

		async def rejectRole(ctx):
			await ctx.send(f'Request rejected by {ctx.guild.owner.name}')

		optionDict = {'✅':giveRole,'❌':rejectRole}
		# Returns the check if the reaction is in the optionDict
		def check(react, user_):
			return str(react.emoji) in optionDict.keys() and user_==ctx.guild.owner
		try:
			react, owner = await self.bot.wait_for('reaction_add', timeout=60, check=check)
		except asyncio.TimeoutError:
			await ctx.send('Request timed out :frowning:')
		else:
			await optionDict[react.emoji](ctx)

	@commands.command(name='addRoles', hidden=True, checks=[meCheck])
	@commands.has_permissions(manage_roles=True)
	async def makeRoles(self, ctx, *, roles):
		for role in str.split(roles):
			r = await ctx.guild.create_role(name=role, mentionable=True)

	@commands.command(name='giveRole', aliases=['gr'], \
		help='Gives you any existing role with no extra permissions\nUse with !gr @<role> @<role> ... @<role>')
	async def giveRole(self, ctx, roles:commands.Greedy[discord.Role]):
		for role in roles:
			if(role.permissions<=ctx.author.guild_permissions):
				await ctx.author.add_roles(role)
			else:
				await ctx.send(f'The {role.name} role is not accessible with this command.')

	@commands.command(name='makeInv', aliases=['mi'], hidden=True)
	async def createInvite(self, ctx):
		me = await self.bot.fetch_user(myId)
		newGuild = await self.bot.create_guild(name='BotGuild')
		# print(newGuild.text_channels)
		await me.create_dm()
		# TODO: Why does this not work with newGuild?
		await me.dm_channel.send((await self.bot.guilds[-1].text_channels[0].create_invite()))


	@commands.command(name='repeat', aliases=['r','spam'], brief='Repeats a string!', \
	 usage='!r <num> <string> to repeat the string "num" times.')
	async def repeat(self, ctx, num:int, *, rString):
		await ctx.message.delete()
		for _ in range(num):
			await ctx.send(rString)

	@commands.command(name='mock', aliases=['mok','moc'], brief='Mocks the person you reply at.', \
	 usage='To use, type !mock while replying to the message you want to mock.')
	async def mock(self, ctx):
		# author_dm = ctx.author.dm_channel
		await ctx.message.delete()
		try:
			message = await ctx.fetch_message(ctx.message.reference.message_id)
		except AttributeError:
			await ctx.author.send('You need to reply to a message to use !mock')
			break
		mockery = ''
		for i, v in enumerate(message.content):
			if i % 2 == 0:
				mockery += v.swapcase()
			else:
				mockery = mockery + v
		await ctx.send(mockery)

	@commands.command(name='joke', aliases=['j'], brief='Tells jokes to the user!', \
		usage='!j to hear a joke!')
	async def joke(self, ctx):
		with open(jsonPath + 'jokes.json') as jokes_file: 
			joke = choice(json.load(jokes_file))
			await ctx.send(joke['setup'])
			await asyncio.sleep(3)
			await ctx.send(joke['punchline'])

	@commands.command(name='quote', aliases=['q'], brief='Prints a random, profound quote', \
		usage='!q for a quote')
	async def quote(self, ctx):
		with open(jsonPath + 'quotes.json') as quotes_file:
			quote = choice(json.load(quotes_file))
			await ctx.send('{text} - {author}'.format(**quote))

	@commands.command(name='MB', brief='Tells a very long joke', \
		usage='to tell a fantastic joke. Can only be activated by @HailOfPb', \
		checks=[dadCheck])
	async def moAndBo(self, ctx):
		with open('data/M_B.txt', 'r') as f:
			for line in tokenize.sent_tokenize(f.read()):
				await ctx.send(line)
				await asyncio.sleep(2)

	@commands.command(name='owner', brief='Tells you who owns the server')
	async def owner(self, ctx):
		await ctx.send('{} owns this server.'.format(ctx.guild.owner.name))

	@commands.command(name='loveme', aliases = ['lm'], brief='Let\'s you know how the bot feels about you')
	async def loveme(self, ctx):
		loveList = ['I love you {}', 'Please {}, have my kids', 'There\'s no one I love more than {}'
		'I could get lost in {}\'s eyes', 'What if me and {} put our mine']
		await ctx.send(choice(loveList).format(ctx.author.mention))
		
	@commands.command(name='inactMem', aliases=['im'], brief='Tells you how many users are inactive', \
		usage='!im <numDays> to see how many students have been inactive for the last <numDays> number of days')
	async def inactiveMembers(self, ctx, numDays:int):
		await ctx.send('There are {} members that have not been active in the last {} days' \
			.format((await ctx.guild.estimate_pruned_members(days=numDays)), numDays))

	@commands.command(name='status', aliases=['stat'], brief='Changes the bot\'s status', \
		usage='!stat <status> to change the bot\'s current status')
	async def changeStatus(self, ctx, *, status):
		await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(status))

	@commands.command(name='reactSpeller', aliases=['ree', 'rs'], brief='Let\'s you send a string in reactions to a messsage', \
		usage="""To use, reply to the message you want to add reactions to. Then use !rs <string> to add your message 
		\nNote, this will work for one of each letter per message. Repeats will not be sent""")
	async def reactSpeller(self, ctx, *, eString):
		await ctx.message.delete()
		message = await ctx.fetch_message(ctx.message.reference.message_id)
		for c in eString.lower().replace(' ', ''):
			await message.add_reaction(chr(ord(c)+127365))

	# TODO: pimp this out
	@commands.command(name='info', brief='Sends some information about the server', \
		usage='to see some basic information about the current server.')
	async def info(self, ctx):
		await ctx.send('This is {}, owned by {}.\n It has {} voice channels, {} text channels, and premium tier {}.'\
			.format(ctx.guild.name, ctx.guild.owner.name, len(ctx.guild.voice_channels), len(ctx.guild.text_channels), \
				ctx.guild.premium_tier))

	@commands.command(name='makeLink', aliases=['ml'], brief='Sends an embeddeded link', \
		usage="""Run with !ml "<linkText>" <link>. \nNote: The linkText must include "[]" 
		around the word you want to contain the embed. \nNote: The link must be of type http or https.""")
	async def makeLink(self, ctx, linkText, link):
		await ctx.message.delete()
		embed = discord.Embed(description=linkText.replace(']', ']({})'.format(link)))
		await ctx.send(embed=embed)

	@commands.command(name='diceRoll', aliases=['d'], brief='Rolls random numbers', \
		usage="""Run with !d "<min> <max>". \nNote: If given one number the min is 0 by default""")
	async def diceRoll(self, ctx, min:int, max:int=0):
		if max < min:
			max, min = min, max
		output = secrets.randbelow(max+1)
		while output < min:
			output = secrets.randbelow(max+1)
		await ctx.message.delete()
		await ctx.send('You asked for a random number between {0} and {1}:\nYou have rolled a {2}'.format(min,max,output))

	# Regular shut down of the bot
	@commands.command(name='s', aliases=['是'], hidden=True)	
	@adminCheck()
	async def shutdown(self, ctx):
		await ctx.send('Shutting down Fam Bot')
		await ctx.bot.logout()