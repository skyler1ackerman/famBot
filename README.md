## FamBot
### A bot for anything I'm feeling like

This bot was started as a pet project to announce Pokemon Go Raids in a Discord server, but quickly evolved as a way to add additional functionality to Discord, as well as a way for me to benefit my friends with dumb projects I've worked on

FamBot has a wide variety of unrealted functionality, as well as a custom help message, and soon, custom error feedback.

## Table of contents

[Setup](#Setup)

[Dependencies](#Dependencies)

[Usage](#Usage)

[Architecture](Architecture)

## Setup

First, you will need to obtain a token for your bot. To do this, go to the [discord developer portal](https://discord.com/developers/docs/intro), make a new application, then create a bot. From there you should be able to grab the token. For a step by step guide, please consult [this page](https://www.writebots.com/discord-bot-token/).

Once you have your discord token, go back to your main directory. Create a file called config.py in the same directory as mainBot.py. Add a single line `TOKEN = <Your Token>`. This should allow you to run your own bot.

Next, install all the [dependencies](#Dependencies). After, run mainBot.py in the main directory. If all has gone well, you should see a message "Fam Bot is online." If not, it's likely that you haven't installed all of the dependencies. 

Now that the bot is running correctly, you'll need to add it to a server to use it. Go back to the developer portal, click your application, and navigate to OAuth2. Click bot in the OAuth2 URL Generator, then in the resulting menu, give the bot whatever permissions you want. I usually make my bot an admin, since I trust my own work. Copy the generated URL, plug it into the browser of your choice, and add the bot to whatever server you so please. Note that you will need the permissions to add the bot to the server. 

Now the bot should be in your server. Give it a whirl by running a few commands. !help is a good place to start.

## Dependencies

Because FamBot has so many functions, FamBot has many dependencies. A (hopefully) full list of dependencies is stored in requirements.txt in the main directory. To download all of them, run `pip install -r requirements.txt`. 

## Usage

The command prefix is currently "!". To run a command, run `!<command>`. I would advise running `!help` to see everything that the bot can do.

## Architecture

The bot is currently split into six different Cogs. This was for organizational purposes. To make a new Cog, please refer to the templete in the templetes folder. 
