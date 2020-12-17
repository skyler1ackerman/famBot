import discord
import asyncio
import time
from datetime import datetime, timedelta, timezone
from discord.ext import commands
from dateutil.parser import parse

raidDict = {}

TIME = 'Time'
INFO = 'Info'
INIT = 'Init'
GOING = 'Going'
NOT_GOING = 'Not_Going'

#TODO: Add a maybe option?

def setup(bot):
	bot.add_cog(EventBot(bot))

class EventBot(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		# Two subroutines for if user is going or not going
		optionDict = {'✅':self.userGoing,'❌':self.userNotGoing}
		# If the message is by a bot, the reaction is not by a bot, and the message is a raid message
		if reaction.message.author.bot and not user.bot and 'New raid:' in reaction.message.content:
			# Call the subroutine with the given emoji
			# TODO: Make this not break for other emojis. Remove them?
			await optionDict[reaction.emoji](reaction.message, user)

	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, user):
		# TODO: Should I remove a person from the list if they unreact?
		print("Reaction Removed")

	@commands.command(name='m')
	async def sendMessage(self, ctx):
		await ctx.send('Hello!')

	@commands.command(name='newRaid', aliases = ['n', 'newraid'], help = 'Command to make a new raid')
	async def newRaid(self, ctx, *input):
		# Use parse to get the datetime object, where ever it is.
		parsedInput = parse(" ".join(input), fuzzy_with_tokens = True)
		# Get the info and time
		info = parsedInput[1][0]
		time = parsedInput[0]
		# Send the very first message
		raidMsg = await ctx.send('New raid: {} \nTime: {} \nInitiator: {}'.format(info, time.strftime('%m-%d-%y %H:%M'), ctx.author.mention))
		# Save the message ID, time, info, init, and make empty going and not going lists.
		raidDict[raidMsg.id] = {TIME: time, INFO: info, INIT: ctx.author, GOING: [], NOT_GOING:[] }
		# Start with two reactions for going and not going
		await raidMsg.add_reaction('✅')
		await raidMsg.add_reaction('❌')

	async def userGoing(self, message, user):
		# If the user isn't already in the going list, add them
		if user not in raidDict[message.id][GOING]:
			raidDict[message.id][GOING].append(user)
		# If the user is in the not going list, remove them
		if user in raidDict[message.id][NOT_GOING]:
			raidDict[message.id][NOT_GOING].remove(user)
		await self.updateMessage(message)

	async def userNotGoing(self, message, user):
		# If the user isn't already in the not going list, add them
		if user not in raidDict[message.id][NOT_GOING]:
			raidDict[message.id][NOT_GOING].append(user)
		# If the user is in the going list, remove them
		if user in raidDict[message.id][GOING]:
			raidDict[message.id][GOING].remove(user)
		await self.updateMessage(message)

	async def updateMessage(self, message):
		# Start with the basic message with info, time, and init
		updatedMessage = 'New raid: {} \nTime: {} \nInitiator: {}' \
		.format(raidDict[message.id][INFO],\
		raidDict[message.id][TIME].strftime('%m-%d-%y %H:%M'), \
		raidDict[message.id][INIT].mention)
		# Add the going list
		updatedMessage += '\nGoing: ' + ', '.join(user.display_name for user in raidDict[message.id][GOING])
		# Add the not going list
		updatedMessage += '\nNot Going: ' + ', '.join(user.display_name for user in raidDict[message.id][NOT_GOING])
		# Update the message
		await message.edit(content=updatedMessage)

# {MID:
# {TIME:<DATETIME>,
# INFO:STRING,
# INIT:USER,
# GOING:[USERS],
# MAYBE:[USERS],
# NOT_GOING:[USERS]
# }
# }