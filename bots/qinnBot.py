import webbrowser
import html5lib
import time
from .common import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from collections import OrderedDict

me = discord.Client()

def setup(bot):
	bot.add_cog(QinnBot(bot))

# # TODO: Cogs inheritance? # I left this here but idk what it means
class QinnBot(commands.Cog, description='Chinese Dictionary Functions'):
	def __init__(self, bot):
# 		# Init the bot
		self.bot = bot


# This is my attempt to salvage my first version of this command. 
#It literally just Let-Me-Google-That-For-Yous the word on Archchinese
	# @commands.command(name='qinLink', aliases=['Qinlink','QinLink','ql','Qlink'], 
	# 	help='Links to a word using the Archchinese online dictionary')
	# async def QLink(self, ctx, char):
	# 	print(str(char))
	# 	# embed = discord.Embed(type='article', description=str(char), 
	# 	# 	url='https://www.archchinese.com/chinese_english_dictionary.html?find='
	# 	# 	+ str(char).strip('\',();'))
	# 	link = 
	# 	embed = discord.Embed(description='[' + str(char) 
	# 		+ '](https://www.archchinese.com/chinese_english_dictionary.html?find=' 
	# 		+ str(char).strip('\',();') +') on Archchinese')
	# 	# print(embed.description, ' and url: ', embed.url)

	# 	await ctx.send(embed=embed)

# snags a URL and returns the "soup"
	def fetchPage(URL):
		options = Options()
		options.headless = True
		driver = webdriver.Firefox()
		driver.get(URL)
		# I had to add this to give the page time to run the js
		time.sleep(1)
		fetchedhtml = driver.page_source
		soup = BeautifulSoup(fetchedhtml, 'html5lib')
		driver.close()
		return soup

# parses the dictionary information for a single char page, currently only from lookup(), and returns a big dict with the fields in it
	def dictEntry(input_string):
		output_List = {}
		input_string = input_string.replace(u'\xa0', u' ')
		input_string = input_string.lstrip('» ')
		for sliced_string in input_string.split('»'):
			output_List[sliced_string[0:sliced_string.index(':')].lstrip(' ')] = sliced_string[sliced_string.index(':'):].lstrip(':  ').strip()
		return output_List

# pulls the info from a single character page and calls dictEntry() on it, returning that
# why are these two functions not combined? I cant remember either, but I did that on purpose a while ago
	def lookup(char):
		URL = 'https://www.archchinese.com/chinese_english_dictionary.html?find=' + str(char).strip('\',();a')
		soup = QinnBot.fetchPage(URL)
		for found_class in soup.find_all(id='charDetailPane') or []:
			for found_div in found_class.find_all(class_='panel-body') or []:
				for character_block in found_class.find_all(id='charDef') or []:
					return QinnBot.dictEntry(character_block.get_text())
		return None

# pulls a whole list of words and their info out of a page and parses them
# does it better
	def itemizeWordsButBetter(*char):
		URL = 'https://www.archchinese.com/chinese_english_dictionary.html?find=' + str(char).strip('\',();a')
		outputList = {}
		soup = QinnBot.fetchPage(URL)
		ITERATOR = -9999
		PINYIN = '!did not assign!'
		DEFINITION = '!did not assign!'
		CHARS = '!did not assign!'
		words_panel = soup.find(id='wordPaneContent').get_text()
		words_panel = words_panel.replace(u'\xa0', u' ')
		# print('\n'+words_panel)
		input_list = words_panel.rsplit(']')
		DEFINITION = input_list[-1].strip()
		del input_list[-1]
		for sliced_string in input_list[::-1]:
			# because of the below line(s) this function will break if the input chars parse into 19+ words
			CHARS = sliced_string[sliced_string.rfind('0' or '1')+2:sliced_string.rfind('[')].strip()
			PINYIN = sliced_string[sliced_string.rfind('[') + 2:None].strip()
			ITERATOR = sliced_string[sliced_string.rfind('0' or '1'):sliced_string.rfind('0' or '1')+2].strip()
			outputList[CHARS] = {'Simplified Form': CHARS, 'Pinyin': PINYIN, 'Definition': DEFINITION, 'Iterator': ITERATOR}
			DEFINITION = sliced_string[1:(sliced_string.rfind('0' or '1') if (sliced_string.rfind('0' or '1')) > 0 else None)].strip()
			# print('\n'+str(sliced_string))		
		# print('\n'+str(outputList))
		return outputList


# discord-callable function to look up a bunch of words and parse them
# needs some keyword arguments or something to include or disinclude info about a word
# use wrappers for this? learn how to use wrappers properly? remember the word "exclude"?
	@commands.command(name='qinnLookup', aliases=['QinnLookup','QinLookup','ql','qinlookup','权利'], 
	help='Looks up Chinese words using the Archchinese online dictionary')
	async def qinnLookup(self, ctx, char):
		output_list = QinnBot.itemizeWordsButBetter(char)
		output_string = str(output_list)
		embed = discord.Embed(colour=discord.Colour.blurple()) #, description=output_string)
		for key in output_list.keys():
			embed.insert_field_at(0,
				name='{0} : {1}'.format(key, output_list.get(key, 'eRrOr').get('Definition', 'bottom level error')), 
				value='{0} Pinyin: {1}'.format(output_list.get(key, 'top level error').get('Iterator', 'bottom level error'), output_list.get(key, 'top level error').get('Pinyin', 'bottom level error')),
				inline=False)
		await ctx.send(embed=embed)

# discord-callable function to look up single character
# is currently broken
	@commands.command(name='qinnChar', aliases=['qinnchar','QinnChar','QinChar','qc','qinchar','清楚'], 
	help='Looks up a single Chinese character using the Archchinese online dictionary')
	async def qinnChar(self, ctx, char):
		print(char)
		output_list = QinnBot.lookup(char[1])
		output_string = str(output_list)
		print(output_list)
		embed = discord.Embed(colour=discord.Colour.blurple()) #, description=output_string)
		embed.add_field(name='{} : {}'.format(char[:1], output_list.get('Definition', 'not found')),
				value='{0} | Subchars: {2} {3} \n Encoding: {1}'.format(output_list.get('Pinyin'), output_list.get('Character Encoding'), output_list.get('Radical').strip('. '), output_list.get('Component').strip('. ')),
				inline=False)
		await ctx.send(embed=embed)








# @TODO await page load

# @TODO formatter function 
# 	intakes Definition or Pinyin and returns the value
# 	implement @lru_cache ? escpecially for dictentry() and fetchpage()


# my hands hold my head
# why did microsoft windows
# change desk.cpl


# reference for lookups

# Definition
# Pinyin
# Radical
# Component
# Traditional Form
# Parts of Speech
# Stroke Count
# Measure Word
# Same Pronunciation
# See Also
# Usage
# Structure
# HSK Level
# Bopomofo (Zhuyin)
# Cantonese (Jyutping)
# Input Method Codes
# Character Encoding
# Formation


	# @commands.command(name='coinToss', aliases=['ct'], help='Flips a coin!')
	# async def coinToss(self, ctx):
	# 	opList = ['Heads!', 'Tails!']
	# 	await ctx.send(choice(opList))

	# @commands.command(name='requestRole', aliases=['rr'], brief='Requests a role', \
	# 	help='Requests a role by sending a dm to the guild owner.')
	# async def requestRole(self, ctx, role:discord.Role):
	# 	await ctx.send('Requesting role, standby')
	# 	await ctx.guild.owner.create_dm()
	# 	reqMsg = await ctx.guild.owner.dm_channel.send("""User {0.author.name} is requesting the {1} role '+ 
	# 		in the {0.guild.name} server""".format(ctx, role.name))
	# 	await reqMsg.add_reaction('✅')
	# 	await reqMsg.add_reaction('❌')

	# 	async def giveRole(ctx):
	# 		await ctx.author.add_roles(role)
	# 		await ctx.send(f'Request approved by {ctx.guild.owner.name}')

	# 	async def rejectRole(ctx):
	# 		await ctx.send(f'Request rejected by {ctx.guild.owner.name}')

	# 	optionDict = {'✅':giveRole,'❌':rejectRole}
	# 	# Returns the check if the reaction is in the optionDict
	# 	def check(react, user_):
	# 		return str(react.emoji) in optionDict.keys() and user_==ctx.guild.owner
	# 	try:
	# 		react, owner = await self.bot.wait_for('reaction_add', timeout=60, check=check)
	# 	except asyncio.TimeoutError:
	# 		await ctx.send('Request timed out :frowning:')
	# 	else:
	# 		await optionDict[react.emoji](ctx)

	# @commands.command(name='addRoles', hidden=True, checks=[meCheck])
	# @commands.has_permissions(manage_roles=True)
	# async def makeRoles(self, ctx, *, roles):
	# 	for role in str.split(roles):
	# 		r = await ctx.guild.create_role(name=role, mentionable=True)

	