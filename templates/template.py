from random import choice
from discord.ext import commands

# This setup function will be called automatically from mainBot if the bot is added to the extensions list
def setup(bot):
	bot.add_cog(TempleteBot(bot))

# This class inherits all of the methods from the Cogs class
class TempleteBot(commands.Cog):
    # Initalize anything you want to
	def __init__(self, bot):
		# Usually a good idea to at least initalize the bot
		self.bot = bot

    # commands wrapper adds the function to the bot commands
    # The name is what the command will be called with. By default is the function name
    # Aliases can also be used to call the command
    # The help parameter will show up if you run the help command on this command specifically
    # Brief will show up in the list when !help COG is run
	@commands.command(name='aCommand', aliases=['ac', 'acom'], help='Helpful comment!', brief='brief description')
	async def aCommandThatIUse(self, ctx):
		await ctx.send('Hello!')

    # This is how you do events in a cog.
    # Note that the below code would cause an infinite loop and should not be used
	@commands.Cog.listener()
    async def on_message(self, message):
        await ctx.send(f'You just sent {message.content}')