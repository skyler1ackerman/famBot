import os
from .common import *
from discord.errors import Forbidden


def setup(bot):
	bot.add_cog(Help(bot))

class Help(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot
		self.bot.remove_command('help')

	#TODO: Set an image
	@commands.command(name='help')
	async def help(self, ctx, *input):
		if not input:
			emb = discord.Embed(title='Commands and Cogs', color=discord.Color.green(), \
				description=f'Use `{self.bot.command_prefix}help <cog>` to gain more information about that Cog!	')

			cogs_desc = ''
			for cog in self.bot.cogs:
				cogs_desc += f'`{cog}` {self.bot.cogs[cog].description}\n'

			emb.add_field(name='Modules', value=cogs_desc, inline=False)

			commands_desc = ''

			for command in self.bot.walk_commands():
			# if cog not in a cog
			# listing command if cog name is None and command isn't hidden
				if not command.cog_name and not command.hidden:
					commands_desc += f'{command.name} - {command.help}\n'

			# adding those commands to embed
			if commands_desc:
				emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

			emb.add_field(name="About", value=f"""This bot is being run by {(await ctx.bot.application_info()).owner.name}. 
				See the source code [here](https://github.com/skyler1ackerman/famBot)""")

			emb.set_footer(text=f"Bot is running {version}")


		elif len(input) == 1:
			def findModule(modName):
				# iterating trough cogs
				for cog in self.bot.cogs:
					# check if cog is the matching one
					if cog.lower() == modName:

						emb = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].description,
							color=discord.Color.blue())

						# getting commands from cog
						for command in self.bot.get_cog(cog).get_commands():
							# if cog is not hidden
							if not command.hidden:
								# TODO: Need this to work with briefs
								emb.add_field(name=f"`{self.bot.command_prefix}{command.name}`", \
									value=command.brief if command.brief else 'No information provided', inline=False)
								# found cog - breaking loop
								emb.set_footer(text=f"To learn more about a command, run {self.bot.command_prefix}help <command>")
						return emb

					else:
						for command in self.bot.get_cog(cog).get_commands():
							if not command.hidden:
								if command.name.lower()==modName or modName in command.aliases:
									# making title - Get the command aliases and description
									emb = discord.Embed(title=f'{command.name}', description=command.brief,
										color=discord.Color.purple())
									allCommands = [command.name] + command.aliases
									emb.add_field(name=f'{command.name} help:', value=f"`[{'|'.join(allCommands)}]` {command.help}")
									return emb

				emb = discord.Embed(title="What's that?!",
						description=f"What are you talking about? `{input[0]}` Doesn't exist. Moron.",
						color=discord.Color.from_rgb(183, 9, 40))

				return emb


			emb = findModule(input[0].lower())



			# if input not found
			# yes, for-loops have an else statement, it's called when no 'break' was issued
			
		elif len(input) > 1:
			emb = discord.Embed(title="Too much requested",
						description="Yo idiot, only ask for one Cog or Command at a time. :rage:",
						color=discord.Color.from_rgb(200,162,200))


		await ctx.send(embed=emb)
