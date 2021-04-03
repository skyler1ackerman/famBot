import discord
import asyncio
import shortuuid
import time
import re
from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from dateutil.parser import parse

shortuuid.set_alphabet('0123456789')

raidDict = {}

# Global Variables
# Dict Keys
MESSAGE = 'Message'
SHORT_ID = 'Short Id'
TIME = 'Time'
INFO = 'Info'
INIT = 'Init'
GOING = 'Going'
NOT_GOING = 'Not_Going'
MAYBE_GOING = 'Maybe Going'
CANCELLED = 'Cancelled'
CHANNEL = 'Channel'
# Emojis
GOING_EMOJI = '✅'
MAYBE_EMOJI = '🟨'
NOT_GOING_EMOJI = '❌'
#TODO: Add a maybe option?

class RaidNotFound(commands.CheckFailure):
	pass

def setup(bot):
	bot.add_cog(RaidBot(bot))

class RaidBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot
		# Start the loop that checks when raids are about to start
		# self.bot.loop.create_task(self.backgroundLoop())
		self.backLoop.start()

	#----------------------------------

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		# Three subroutines for if user is going, maybe going, or not going
		optionDict = {GOING_EMOJI:GOING, MAYBE_EMOJI: MAYBE_GOING, NOT_GOING_EMOJI:NOT_GOING}
		# If the message is by a bot, the reaction is not by a bot, and the message is a raid message
		if reaction.message.author.bot and not user.bot and reaction.message.content.startswith('Raid '):
			if optionDict.get(reaction.emoji):
				await self.updateList(reaction.message, user, optionDict[reaction.emoji])
			else:
				await reaction.message.remove_reaction(reaction.emoji, user)
			# Call the subroutine with the given emoji
			
	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, user):
		# Three subroutines for if user renegs going, maybe going, or not going
		optionDict = {GOING_EMOJI:GOING, MAYBE_EMOJI: MAYBE_GOING, NOT_GOING_EMOJI:NOT_GOING}
		# If the message is by a bot, the reaction is not by a bot, and the message is a raid message
		if reaction.message.author.bot and not user.bot and reaction.message.content.startswith('Raid '):
			if optionDict.get(reaction.emoji):
				# Call the subroutine with the given emoji
				await self.updateListRemove(reaction.message, user, optionDict[reaction.emoji])
			
	@commands.command(name='newRaid', aliases = ['n', 'newraid', 'raid'], help = 'Command to make a new raid. Try typing "!n Weedle Raid at the Fountain 3:00 pm"')
	async def newRaid(self, ctx, *input):
		# Use parse to get the datetime object, where ever it is.
		parsedInput = parse(' '.join(input), fuzzy_with_tokens = True)
		# Get the info and time
		info = re.sub(' +', ' ', " ".join(parsedInput[1]))
		time = parsedInput[0]
		shortID = await self.createURID()
		# Send the very first message
		raidMsg = await ctx.send('Raid {}: {} \nTime: {} \nInitiator: {}'.format(shortID, info, time.strftime('%m-%d-%y %H:%M'), ctx.author.mention))
		# Should I add this line? It stays behind when the raid is gone, which isn't great
		# await ctx.send('_ _')
		# Save the message with all of the extra info
		raidDict[raidMsg.id] = {MESSAGE: raidMsg, SHORT_ID: shortID, TIME: time, INFO: info, \
		INIT: ctx.author, GOING: [], MAYBE_GOING: [], NOT_GOING:[], CHANNEL: ctx.channel, CANCELLED: False}
		# Delete the command message
		await ctx.message.delete()
		# Start with thre reactions for going, maybe going, and not going
		await raidMsg.add_reaction(GOING_EMOJI)
		await raidMsg.add_reaction(MAYBE_EMOJI)
		await raidMsg.add_reaction(NOT_GOING_EMOJI)


	@commands.command(name='c')
	async def printCTXDIR(self,ctx):
		await ctx.send(dir(ctx))

	# This is called if a user removes their emoji from a message
	async def updateListRemove(self, message, user, statusKey):
		# Simply remove their name from the given list if they are on the list
		if user in raidDict[message.id][statusKey]:
			raidDict[message.id][statusKey].remove(user)
		await self.updateMessage(message)

	# This is called when a user reacts to a raid
	async def updateList(self, message, user, statusKey):
		optionList = [GOING, NOT_GOING, MAYBE_GOING]
		# If the user isn't already in the given list, add them
		if user not in raidDict[message.id][statusKey]:
			raidDict[message.id][statusKey].append(user)
		shortList = [op for op in optionList if op != statusKey]
		# If the user had already selected one of the other options, remove them
		for option in shortList:
			if user in raidDict[message.id][option]:
				raidDict[message.id][option].remove(user)
		await self.updateMessage(message)

	# This is called after the list is updated so we can also update the message
	async def updateMessage(self, message):
		# Create the base message with all of the formatting arranged.
		baseMsg = 'Raid {}: {} \nTime: {} \nInitiator: {}'
		# Mark as cancelled if the raid is cancelled
		if raidDict[message.id][CANCELLED]:
			baseMsg = 'Cancelled ' + baseMsg
		# Start with the basic message with info, time, and init
		updatedMessage =  baseMsg \
		.format(raidDict[message.id][SHORT_ID],\
		raidDict[message.id][INFO],\
		raidDict[message.id][TIME].strftime('%m-%d-%y %H:%M'), \
		raidDict[message.id][INIT].mention)
		# Add the going list
		updatedMessage += '\nGoing: ' + ', '.join(user.display_name for user in raidDict[message.id][GOING])
		# Add the maybe going list
		updatedMessage += '\nMaybe Going: ' + ', '.join(user.display_name for user in raidDict[message.id][MAYBE_GOING])
		# Add the not going list
		updatedMessage += '\nNot Going: ' + ', '.join(user.display_name for user in raidDict[message.id][NOT_GOING])
		# Update the message
		if raidDict[message.id][CANCELLED]:
			await message.clear_reactions()
			updatedMessage += '\n -- CANCELLED -- '
		await message.edit(content=updatedMessage)

	# Used to create unique ID for each raid
	async def createURID(self):
		# The odds of a raid being a duplicate is pretty low but we have this loop just in case
		while True:
			# Six digits seemed good
			shortID = shortuuid.uuid()[0:6]
			if shortID not in raidDict:
				return shortID

	@commands.command(name='cancel', help='Cancel a raid by raid ID. Call with !cancel <RaidId>')
	async def cancelRaid(self, ctx, ID):
		raid = await self.getRaidByURID(ID)
		raid[CANCELLED] = True
		await ctx.message.delete()
		await self.updateMessage(raid[MESSAGE])

	# A pretty basic function that finds a raid in the raidDict using it's URID
	async def getRaidByURID(self, ID):
		for raid in raidDict.values():
			if raid[SHORT_ID] == ID:
				return raid
		raise RaidNotFound('We cannot find that raid!')

	# Error handling for any function that looks for raids
	@cancelRaid.error
	async def testError(self, ctx, error):
		if isinstance(error, RaidNotFound):
			await ctx.send(error)

	# TODO: Split delete and ping into two seperate functions?
	@tasks.loop(minutes=1)
	async def backLoop(self):
		await self.bot.wait_until_ready()
		delList = []
		# Loop through all of the current raid messages
		for raid in raidDict.values():
			# If the raid is between 5 and 6 minutes away, ping everyone who is going that it's starting soon
			if raid[TIME]-timedelta(minutes=6) <= datetime.now() <= raid[TIME]-timedelta(minutes=5) and raid[GOING]:
				await raid[CHANNEL].send(', '.join(u.mention for u in raid[GOING]) + ', ' + raid[INFO] + ' is starting in five minutes!')
			# If the raid has passed, prep it for deletion
			if raid[TIME] <= datetime.now():
				delList.append(raid[MESSAGE].id)
		# If the raid has been prepped for deletion
		for delM in delList:
			# Delete the message
			await raidDict[delM][MESSAGE].delete()
			# Delete the raid from the dictionary
			raidDict.pop(delM)

# {MID:
# {TIME:<DATETIME>,
# INFO:STRING,
# INIT:USER,
# GOING:[USERS],
# MAYBE:[USERS],
# NOT_GOING:[USERS]
# }
# }