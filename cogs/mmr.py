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

        dic = {
            0: "Unranked",
            1: "Unranked",
            3: "Iron 1",
            4: "Iron 2",
            5: "Iron 3",
            6: "Bronze 1",
            7: "Bronze 2",
            8: "Bronze 3",
            9: "Silver 1",
            10: "Silver 2",
            11: "Silver 3",
            12: "Gold 1",
            13: "Gold 2",
            14: "Gold 3",
            15: "Platin 1",
            16: "Platin 2",
            17: "Platin 3",
            18: "Diamond 1",
            19: "Diamond 2",
            20: "Diamond 3",
            21: "Immortal 1",
            22: "Immortal 2",
            23: "Immortal 3",
            24: "Radiant"
        }
        if not name:
            
            try:
                user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
                username = user['username']
                password = user['password']
                region   = user['region']
                user_data = username_to_data(username, password)
                user_id = user_data[2]
                mmrHistory = getMMRHistory(region, user_id, user_data[0], user_data[1], 5)


                for i in mmrHistory["Matches"]:
                    rank =i["TierAfterUpdate"]
                    mmr = i["RankedRatingAfterUpdate"]
                    change = i["RankedRatingEarned"]
                    performance = i["RankedRatingPerformanceBonus"]
                    date = i["MatchStartTime"]
                    
                    if change < 0:
                        colorx = discord.Color.red()
                    else:
                        colorx = discord.Color.green()
                        change = f"+{change}"
                        
                    rr = f"**{mmr} / 100** RR"
                    change = f"**{change}** - Performance {performance}"
                        
                    embed = discord.Embed(
                        title=dic[rank],
                        color = colorx,
                        timestamp= datetime.fromtimestamp(date//1000)
                    )

                    embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{rank}.png")
                    embed.add_field(name="Rank Rating",value=rr,inline=False)
                    embed.add_field(name="Change", value=change, inline=False)
                    
                    footer = (
                        "🟢 gespielt"
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
                    for i in mmrHistory["Matches"]:
                        rank = i["TierAfterUpdate"]
                        mmr = i["RankedRatingAfterUpdate"]
                        change = i["RankedRatingEarned"]
                        performance = i["RankedRatingPerformanceBonus"]
                        date = i["MatchStartTime"]

                        if change < 0:
                            colorx = discord.Color.red()
                        else:
                            colorx = discord.Color.green()
                            change = f"+{change}"

                        rr = f"**{mmr} / 100** RR"
                        change = f"**{change}** - Performance {performance}"

                        embed = discord.Embed(
                            title=dic[rank],
                            color=colorx,
                            timestamp=datetime.fromtimestamp(date // 1000)
                        )

                        embed.set_thumbnail(
                            url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{rank}.png")
                        embed.add_field(name="Rank Rating", value=rr, inline=False)
                        embed.add_field(name="Change", value=change, inline=False)

                        footer = (
                            "🟢 gespielt"
                        )
                        embed.set_footer(text=footer)

                        await ctx.send(embed=embed)
                       
            except Exception as e:
                print(e)
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

