import os
from .common import *

# Custom Errors
class NotAnAdmin(commands.CheckFailure):
	pass

def setup(bot):
	bot.add_cog(imgBot(bot))

class imgBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot

	@commands.command(name='saveImg', brief='Saves an image to the reactions folder to use later', \
		help="""Run the command !si <imgName>. Attach the image you want to be saved with with given name.\n
		Please have the name be three characters for simplicity""", aliases=['si'])
	async def imageSaver(self, ctx, imgName):
		# if len(imgName) != 3:
		# 	await ctx.send('Please have a title of exactly 3 characters')
		# 	return
		for attach in ctx.message.attachments:
			if  not any(attach.filename.lower().endswith(image) for image in image_types):
				await ctx.send('Image format not recognized')
				return
			_, file_ext = os.path.splitext(attach.filename)
			await attach.save(reactPath+imgName+file_ext)
			await ctx.send(f'Image saved as {imgName+file_ext}')

	@commands.command(name='listImg', brief='Lists all images currently in the reaction folder', aliases=['li'])
	async def listImages(self, ctx):
		sendStr = []
		for img in os.listdir(reactPath):
			sendStr.append(os.path.splitext(img)[0])
		await ctx.send(', '.join(sendStr))

	@commands.command(name='img', brief='Send a reaction image.', help='Run !li to list all options')
	async def imgSender(self, ctx, react):
		allImg = [img for img in os.listdir(reactPath) if os.path.splitext(img)[0]==react]
		if len(allImg) > 1:
			await ctx.send('There was more than one image found!')
		elif not allImg:
			await ctx.send('There were no images found with that name.')
		else:
			await ctx.send(file=discord.File(reactPath+allImg[0]))
