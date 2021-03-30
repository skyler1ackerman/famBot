import discord, json, cv2
from discord.ext import commands
from scipy.ndimage import rotate

# Custom Errors
class NotAnAdmin(commands.CheckFailure):
	pass

def setup(bot):
	bot.add_cog(imgBot(bot))

class imgBot(commands.Cog):
	def __init__(self, bot):
		# Init the bot
		self.bot = bot
		self.image_types = ["png", "jpeg", "gif", "jpg"]

	# Custom Error Checking
	def adminCheck():
		async def adminError(ctx):
			if not ctx.author.guild_permissions.administrator:
				raise NotAnAdmin('You are not an admin!')
			return True
		return commands.check(adminError)

	@commands.Cog.listener()
	async def on_message(self, message):
		image_types = ["png", "jpeg", "gif", "jpg"]
		for attach in message.attachments:
			if any(attach.filename.lower().endswith(image) for image in image_types) and not message.author.bot:
				await attach.save('./data/' + attach.filename)
				# await message.channel.send(file=discord.File(attach.filename))

	@commands.command(name='img')
	async def imgSender(self, ctx, react):
		# TODO: Have this work for all image types
		await ctx.send(file=discord.File('./data/images/reactions/' + react + '.png'))
		await ctx.message.delete()

	@commands.command(name='rotate', aliases=['rot'])
	async def rotator(self, ctx, angle):
		for attach in ctx.message.attachments:
			if any(attach.filename.lower().endswith(image) for image in self.image_types) and not ctx.author.bot:
				await attach.save('./data/images/' + attach.filename)
				img = cv2.imread('./data/images/'+ attach.filename)
				print(img.shape)
				img2 = rotate(img, 90)
				print(img2.shape)
				# Why does this not write out how I think it should?
				cv2.imwrite('.data/images/newtree.jpg', img2)