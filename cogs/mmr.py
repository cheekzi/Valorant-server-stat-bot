import discord
from discord.ext import commands
import requests
import json 
from .utils.rank_utils import username_to_data,getMMRHistory, getMMRHistory_name
from discord_components import *
from datetime import datetime

with open ('././config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    prefix = config['prefix']

class mmr(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def mmr(self, ctx, *, name=None):
        author_id = str(ctx.author.id)
        
        if not name:
            
            try:
                user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
                username = user['username']
                password = user['password']
                region   = user['region']
                user_data = username_to_data(username, password)
                user_id = user_data[2]
                mmrHistory = getMMRHistory(region, user_id)
                for i in range(5):
                    rank = mmrHistory["data"][i]["currenttierpatched"]
                    raw_rank = mmrHistory["data"][i]["currenttier"]
                    mmr = mmrHistory["data"][i]["ranking_in_tier"]
                    change = mmrHistory["data"][i]["mmr_change_to_last_game"]
                    date = mmrHistory["data"][i]["date_raw"]
                    
                    if change < 0:
                        colorx = discord.Color.red()
                    else:
                        colorx = discord.Color.green()
                        change = f"+{change}"
                        
                    rr = f"**{mmr} / 100** RR            - **{change}**"
                        
                    print(str(datetime.fromtimestamp(int(date))))
                    embed = discord.Embed(
                        title=rank,
                        color = colorx,
                        timestamp= datetime.fromtimestamp(int(date)//1000)
                    )

                    embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{raw_rank}.png")
                    embed.add_field(name="Rank Rating",value=rr,inline=False)


                    footer = (
                        f"🟢 <t:{date}:F>"
                    )
                    embed.set_footer(text=footer)
                    await ctx.send(embed=embed)
            
            except Exception as e:
                print(e)
                embed= discord.Embed(
                    color=discord.Color.red()
                )
                embed.add_field(name ="SOME ERROR OCCURED...",value="""
                Couldn't find statistics. \n You have to be `logged in`to use this command \n Otherwise try using **!mmr <name#tag>** to view anyone's statistics.
                """,inline=False)
                embed.set_thumbnail(url="https://i.imgur.com/A45DVhf.gif")
                await ctx.send(
                    embed=embed
                )
        else:
            print(name)
            username = name.split('#')
            tag=username[1]
            username = username[0]
            
            try:
                mmrHistory = getMMRHistory_name(username, tag)
                for i in range(5):
                    rank = mmrHistory["data"][i]["currenttierpatched"]
                    raw_rank = mmrHistory["data"][i]["currenttier"]
                    mmr = mmrHistory["data"][i]["ranking_in_tier"]
                    change = mmrHistory["data"][i]["mmr_change_to_last_game"]
                    date = mmrHistory["data"][i]["date_raw"]
                    
                    if change < 0:
                        colorx = discord.Color.red()
                    else:
                        colorx = discord.Color.green()
                        change = f"+{change}"
                        
                    rr = f"**{mmr} / 100** RR            - **{change}**"
                        
                    embed = discord.Embed(
                        title=rank,
                        color = colorx,
                        timestamp= datetime.fromtimestamp(int(date)//1000)
                    )
                    embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{raw_rank}.png")
                    embed.add_field(name="Rank Rating",value=rr,inline=False)
                    embed.add_field(name="Rank Rating",value=f"🟢 <t:{date}:F>",inline=False)

                    footer = (
                        f"🟢 <t:{date}:F>"
                    )
                    embed.set_footer(text=footer)
                    await ctx.send(embed=embed)
                       
            except Exception as e:
                print(e)
                if str(e) == "'data'":
                    embed= discord.Embed(
                        color=discord.Color.red()
                    )
                    embed.add_field(name ="SOME ERROR OCCURED...",value=f"""
                    Couldn't find statistics for `{name}` \n Check if the name is correct and try again later.
                    """,inline=False)
                    embed.set_thumbnail(url="https://i.imgur.com/A45DVhf.gif")
                    await ctx.send(
                        embed=embed
                    )

def setup(client):
    client.add_cog(mmr(client))
    print("recentMMR         | Imported") 

