import discord
from discord.ext import commands
import traceback
import sys
import os
import json 
import requests
from discord_components import *
from datetime import date

#for database
import asyncpg
from asyncpg.pool import create_pool
import sqlite3


with open ('config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    token = config['token']
    prefix = config['prefix']
    database_url = config['database_url']



bot = commands.Bot(command_prefix=f'{prefix}') #defining bot prefix 

bot.remove_command('help')


async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(f"{database_url}")
    print("DATABASE     | Connected")


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online, 
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{prefix}help")
    )
    print("Bot online!")
    DiscordComponents(bot)



with open ('extension/extension.json', 'r') as data:
    cog_data = json.load(data, strict=False)
    extensions = cog_data['extension']

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except:
            print(f'Error loading {extension}', file=sys.stderr)
            traceback.print_exc()

current_date = date.today().strftime("%d")
if int(os.environ['HEROKU_PLAT']) == 1 and current_date < 25:
    bot.loop.run_until_complete(create_db_pool())
    bot.run(os.environ['DISCORD_TOKEN'])
elif int(os.environ['HEROKU_PLAT']) == 2 and current_date >= 25:
    bot.loop.run_until_complete(create_db_pool())
    bot.run(os.environ['DISCORD_TOKEN'])
else:
    print("nicht aktiv " + current_date + os.environ['HEROKU_PLAT'])
