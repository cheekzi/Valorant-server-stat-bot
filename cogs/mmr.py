import discord
from discord.ext import commands
import requests
import json 
from .utils.rank_utils import username_to_data,getMMRHistory
from discord_components import *

with open ('././config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    prefix = config['prefix']

class mmr(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def mmr(self, ctx, name:str):
        author_id = str(ctx.author.id)
        
        if not name:
            user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
            username = user['username']
            password = user['password']
            region   = user['region']
            
            try:
                user_data = username_to_data(username, password)
                user_id = user_data[2]
                mmrHistory = getMMRHistory(region, user_id)
                for i in range(5):
                    rank = mmrHistory["data"][i]["currenttierpatched"]
                    mmr = mmrHistory["data"][i]["ranking_in_tier"]
                    change = mmrHistory["data"][i]["mmr_change_to_last_game"]
                    ctx.send(rank + str(mmr) + str(change))
            
            except Exception as e:
                print(e)
        else:
            username = message.content.split('#')
            name=username[0]
            tag=username[1]
            
            try:
                mmrHistory = getMMRHistory_name(name, tag)
                for i in range(5):
                    rank = mmrHistory["data"][i]["currenttierpatched"]
                    mmr = mmrHistory["data"][i]["ranking_in_tier"]
                    change = mmrHistory["data"][i]["mmr_change_to_last_game"]
                    ctx.send(rank + str(mmr) + str(change))

def setup(client):
    client.add_cog(recentMMR(client))
    print("recentMMR         | Imported") 

