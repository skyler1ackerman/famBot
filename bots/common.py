from discord.ext import commands
from config import DAD_ID
import discord, json

# FILE PATHS
jsonPath = 'data/json/'
reactPath = 'data/images/reactions/'

# TODO: Send back user feedback on error
# Use discord.commands.on_error probs
image_types = ["png", "jpeg", "gif", "jpg"]


async def meCheck(ctx):
	appInfo = await ctx.bot.application_info()
	return ctx.author.id == appInfo.owner.id

# Generic checks
async def dadCheck(ctx):
	return ctx.author.id == DAD_ID

class NotAnAdmin(commands.CheckFailure):
	pass

class NotOwner(commands.CheckFailure):
	pass

# Custom Error Checking
def adminCheck():
	async def adminError(ctx):
		if not ctx.author.guild_permissions.administrator:
			raise NotAnAdmin('You are not an admin!')
		return True
	return commands.check(adminError)
