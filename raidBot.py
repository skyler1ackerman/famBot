import discord
import asyncio
import time
import re
from datetime import datetime, timedelta, timezone
from discord.ext import commands
from dateutil.parser import parse

raidDict = {}

# Global Variables
# Dict Keys
MESSAGE = 'Message'
TIME = 'Time'
INFO = 'Info'
INIT = 'Init'
GOING = 'Going'
NOT_GOING = 'Not_Going'
MAYBE_GOING = 'Maybe Going'
CHANNEL = 'Channel'
# Emojis
GOING_EMOJI = '✅'
MAYBE_EMOJI = '🟨'
NOT_GOING_EMOJI = '❌'
#TODO: Add a maybe option?

def setup(bot):
	bot.add_cog(RaidBot(bot))

class RaidBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot
		# Start the loop that checks when raids are about to start
		self.bot.loop.create_task(self.backgroundLoop())

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		# Three subroutines for if user is going, maybe going, or not going
		optionDict = {GOING_EMOJI:GOING, MAYBE_EMOJI: MAYBE_GOING, NOT_GOING_EMOJI:NOT_GOING}
		# If the message is by a bot, the reaction is not by a bot, and the message is a raid message
		if reaction.message.author.bot and not user.bot and 'New raid:' in reaction.message.content:
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
		if reaction.message.author.bot and not user.bot and 'New raid:' in reaction.message.content:
			if optionDict.get(reaction.emoji):
				# Call the subroutine with the given emoji
				await self.updateListRemove(reaction.message, user, optionDict[reaction.emoji])
			
	@commands.command(name='newRaid', aliases = ['n', 'newraid'], help = 'Command to make a new raid. Try typing "!n Weedle Raid at the Fountain 3:00 pm"')
	async def newRaid(self, ctx, *input):
		# Use parse to get the datetime object, where ever it is.
		parsedInput = parse(' '.join(input), fuzzy_with_tokens = True)
		# Get the info and time
		info = re.sub(' +', ' ', " ".join(parsedInput[1]))
		time = parsedInput[0]
		# Send the very first message
		raidMsg = await ctx.send('New raid: {} \nTime: {} \nInitiator: {}'.format(info, time.strftime('%m-%d-%y %H:%M'), ctx.author.mention))
		# Save the message ID, time, info, init, and make empty going and not going lists.
		raidDict[raidMsg.id] = {MESSAGE: raidMsg, TIME: time, INFO: info, INIT: ctx.author, GOING: [], MAYBE_GOING: [], NOT_GOING:[], CHANNEL: ctx.channel}
		# Start with thre reactions for going, maybe going, and not going
		await raidMsg.add_reaction(GOING_EMOJI)
		await raidMsg.add_reaction(MAYBE_EMOJI)
		await raidMsg.add_reaction(NOT_GOING_EMOJI)		

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
		for option in shortList:
			if user in raidDict[message.id][option]:
				raidDict[message.id][option].remove(user)
		await self.updateMessage(message)

	# This is called after the list is updated so we can also update the message
	async def updateMessage(self, message):
		# Start with the basic message with info, time, and init
		updatedMessage = 'New raid: {} \nTime: {} \nInitiator: {}' \
		.format(raidDict[message.id][INFO],\
		raidDict[message.id][TIME].strftime('%m-%d-%y %H:%M'), \
		raidDict[message.id][INIT].mention)
		# Add the going list
		updatedMessage += '\nGoing: ' + ', '.join(user.display_name for user in raidDict[message.id][GOING])
		# Add the maybe going list
		updatedMessage += '\nMaybe Going: ' + ', '.join(user.display_name for user in raidDict[message.id][MAYBE_GOING])
		# Add the not going list
		updatedMessage += '\nNot Going: ' + ', '.join(user.display_name for user in raidDict[message.id][NOT_GOING])
		# Update the message
		await message.edit(content=updatedMessage)

	# This is the loop that runs in the background.
	# Right now it does two things, checks if a raid is 5 min away from starting, or if a raid is over.
	async def backgroundLoop(self):
		# Loop infinitely
		while True:
			# This is the list of messages to delete each iteration
			# We reset it ever loop
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
			# Sleep for a minute
			await asyncio.sleep(60)

# {MID:
# {TIME:<DATETIME>,
# INFO:STRING,
# INIT:USER,
# GOING:[USERS],
# MAYBE:[USERS],
# NOT_GOING:[USERS]
# }
# }