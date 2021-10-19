import shortuuid, emoji
from discord.ext import commands
from .common import *

def setup(bot):
	bot.add_cog(PollBot(bot))

class PollBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot
		self.polls = []

	class Poll():

		class Option():
			def __init__(self, value, emoji, poll):
				self.value = value
				self.votes = []
				self.emoji = emoji
				self.poll = poll

			def __eq__(self, emoji):
				return self.emoji==emoji

			def __str__(self):
				return f'{self.emoji} {self.value}'

		def __init__(self, title, options):
			self.title = title
			self.options = [self.Option(o, chr(i+127365+97), self) for i, o in enumerate(options)]
			self.id = shortuuid.uuid()[:6]
			self.embed = self.makeEmbed()
			self.message = None

		def __eq__(self, oId):
			return oId == self.id or oId.id ==self.id

		def __ne__(self, oPoll):
			return oPoll.id !=self.id

		def __getitem__(self, idx):
			return self.options[idx]

		def makeEmbed(self):
			emb = discord.Embed(title=f'Poll {self.id}: {self.title}\n', color=discord.Color.purple())
			optMessage = ''
			for o in self.options:
				optMessage+=f'{o.emoji} {o.value}: **{len(o.votes)} Votes**\n'
			emb.add_field(name='Options', value=optMessage, inline=False)
			return emb

	@commands.command(name='poll', brief='Create a new poll', help="""Create a poll with a question on the first line, 
		then each option on a new line""")
	async def makePoll(self, ctx, *, pollList):
		pollList = pollList.split('\n')
		title, pollList = pollList[0], pollList[1:]
		testPoll = self.Poll(title, pollList)
		testPoll.message = await ctx.send(embed=testPoll.embed)

		for i in range(len(testPoll.options)):
			await testPoll.message.add_reaction(chr(i+127365+97))
		self.polls.append(testPoll)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if (id_:=reaction.message.embeds[0].title[5:11]) in self.polls:
			option = self.polls[self.polls.index(id_)][reaction.message.reactions.index(reaction)]
			option.votes.append(user)
			await reaction.message.edit(embed=option.poll.makeEmbed())

	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, user):
		if (id_:=reaction.message.embeds[0].title[5:11]) in self.polls:
			option = self.polls[self.polls.index(id_)][reaction.message.reactions.index(reaction)]
			option.votes.remove(user)
			await reaction.message.edit(embed=option.poll.makeEmbed())



	# Send a list to the list
	# List out the options with a letter for each
	# If user reacts to message, tally the vote
	# If user unreacts, retract the vote
	# Graph the results
	# MAke prettier - Code in add and removes
