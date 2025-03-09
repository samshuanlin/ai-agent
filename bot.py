import os
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv
from agent import MistralAgent
from meme_api import MemeAPI
from x_rotd import X_ROTD

PREFIX = "!"

# Setup logging
logger = logging.getLogger("discord")

# Load the environment variables
load_dotenv()

# Create the bot with all intents
# The message content and members intent must be enabled in the Discord Developer Portal for the bot to work.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Import the Mistral agent from the agent.py file
agent = MistralAgent()

# Import the MemeAPI agent
meme_api = MemeAPI()

x_rotd = X_ROTD()

# Get the token from the environment variables
token = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    """
    Called when the client is done preparing the data received from Discord.
    Prints message on terminal when bot successfully connects to discord.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
    """
    logger.info(f"{bot.user} has connected to Discord!")


@bot.event
async def on_message(message: discord.Message):
    """
    Called when a message is sent in any channel the bot can see.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_message
    """
    # Don't delete this line! It's necessary for the bot to process commands.
    await bot.process_commands(message)

    # Ignore messages from self or other bots to prevent infinite loops.
    if message.author.bot or message.content.startswith("!"):
        return

    # Process the message with the agent you wrote
    # Open up the agent.py file to customize the agent
    logger.info(f"Processing message from {message.author}: {message.content}")
    response = await agent.run(message)

    # Send the response back to the channel
    await message.reply(response)

@bot.command(name="send_image", help="sends an image")
async def send_image(ctx, *, arg=None):
    # Get the meme data
    meme_data = meme_api.get_meme()
    image_url = meme_data["url"]
    await ctx.send(image_url)

@bot.command(name="rotd", help="gives rizz of the day")
async def give_rotd(ctx, *, arg=None):
    flirtatious_tweet = x_rotd.get_most_flirtatious_tweet()
    print(flirtatious_tweet)
    await ctx.send(flirtatious_tweet['tweet'])


@bot.command(name="send_sticker1", help="sends sticker 1: +1000 aura")
async def send_image(ctx, *, arg=None):
    # Get the meme data
    image = "1.png"
    await ctx.send(file=discord.File(image))


# Commands


# This example command is here to show you how to add commands to the bot.
# Run !ping with any number of arguments to see the command in action.
# Feel free to delete this if your project will not need commands.
@bot.command(name="ping", help="Pings the bot.")
async def ping(ctx, *, arg=None):
    if arg is None:
        await ctx.send("Pong!")
    else:
        await ctx.send(f"Pong! Your argument was {arg}")


# Start the bot, connecting it to the gateway
bot.run(token)
