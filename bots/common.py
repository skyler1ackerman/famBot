from discord.ext import commands
import discord, json

# FILE PATHS
jsonPath = 'data/json/'
# TODO: Send back user feedback on error
# Use discord.commands.on_error probs
# TODO: Add a dad check
async def meCheck(ctx):
	appInfo = await ctx.bot.application_info()
	return ctx.author.id == appInfo.owner.id

async def dadCheck(ctx):
	return ctx.author.id == 575872224620183553

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
