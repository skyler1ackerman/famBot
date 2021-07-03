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

class QinnBot(commands.Cog, description='Chinese Dictionary Functions'):
	def __init__(self, bot):
		self.bot = bot

# snags a URL and returns the "soup"
	def fetchPage(URL):
		options = Options()
		options.headless = True
		driver = webdriver.Firefox(options=options)
		driver.get(URL)
		# I had to add this to give the page time to run the js
		# use https://www.selenium.dev/documentation/en/webdriver/waits/ later to fix this
		time.sleep(0.5)
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
		if len(str(char)) < 1:
			raise ValueError
		URL = 'https://www.archchinese.com/chinese_english_dictionary.html?find=' + str(char).strip('\',();a')
		soup = QinnBot.fetchPage(URL)
		for found_class in soup.find_all(id='charDetailPane') or []:
			for found_div in found_class.find_all(class_='panel-body') or []:
				for character_block in found_class.find_all(id='charDef') or []:
					return QinnBot.dictEntry(character_block.get_text())
		return None

# pulls a whole list of words and their info out of a page and parses them
	def itemizeWordsButBetter(*char):
		print(str(char))
		if len(str(char).replace(',','')) <= 1:
			return QinnBot.lookup(char)
			pass
		URL = 'https://www.archchinese.com/chinese_english_dictionary.html?find=' + str(char).strip('\',();a')
		outputList = {}
		soup = QinnBot.fetchPage(URL)
		ITERATOR = -9999
		PINYIN = '!did not assign!'
		DEFINITION = '!did not assign!'
		CHARS = '!did not assign!'
		words_panel = soup.find(id='wordPaneContent').get_text()
		words_panel = words_panel.replace(u'\xa0', u' ')
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
		return outputList

# discord-callable function to look up a bunch of words and parse them
# needs some keyword arguments or something to include or disinclude info about a word
# use wrappers for this? learn how to use wrappers properly? remember the word "exclude"?
	@commands.command(name='qinnLookup', aliases=['QinnLookup','QinLookup','ql','qinlookup','权利'], 
	help='Looks up Chinese words using the Archchinese online dictionary')
	async def qinnLookup(self, ctx, char):
		output_list = QinnBot.itemizeWordsButBetter(char)
		output_string = str(output_list)
		embed = discord.Embed(colour=discord.Colour.blurple())
		for key in output_list.keys():
			embed.insert_field_at(0,
				name='{0} : {1}'.format(key, output_list.get(key, 'eRrOr').get('Definition', 'bottom level error')), 
				value='{1}'.format(output_list.get(key, 'top level error').get('Iterator', 'bottom level error'), output_list.get(key, 'top level error').get('Pinyin', 'bottom level error')),
				inline=False)
		await ctx.send(embed=embed)

# discord-callable function to look up single character
	@commands.command(name='qinnChar', aliases=['qinnchar','QinnChar','QinChar','qc','qinchar','清楚'], 
	help='Looks up a single Chinese character using the Archchinese online dictionary')
	async def qinnChar(self, ctx, chars):
		print(chars)
		for single_char in chars:
			output_list = QinnBot.lookup(single_char)
			output_string = str(output_list)
			print(output_list)
			embed = discord.Embed(colour=discord.Colour.blurple()) #, description=output_string)
			embed.add_field(name='{} : {}'.format(single_char[:1], output_list.get('Definition', 'not found')),
					value='{0}  |  Subchars: {2} {3}  |  Part of: {4}\n Encoding: {1}'.format(output_list.get('Pinyin'), output_list.get('Character Encoding'), str(output_list.get('Radical')).strip('. '), str(output_list.get('Component')).strip('. '), str(output_list.get('Part of')).strip('. ')),
					inline=False)
			await ctx.send(embed=embed)