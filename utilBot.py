import discord
from discord.ext import commands

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

	@commands.command(name='repeat', aliases=['r'])
	async def repeat(self, ctx, rString, num):
		for x in range(int(num)):
			await ctx.send(rString)

	# Regular shut down of the bot
	@commands.command(name='s')
	@adminCheck()
	async def shutdown(self, ctx):
		await ctx.send('Shutting down Fam Bot')
		await ctx.bot.logout()