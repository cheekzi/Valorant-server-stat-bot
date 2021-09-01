import discord
from discord.ext import commands
import requests
import json 
from utils.graph_utils as val 
from discord_components import *
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import os

with open ('././config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    prefix = config['prefix']

class graph(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def graph(self, ctx, *, name=None):
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
                        
                    embed = discord.Embed(
                        title=rank,
                        color = colorx,
                        timestamp= datetime.fromtimestamp(date//1000)
                    )

                    embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{raw_rank}.png")
                    embed.add_field(name="Rank Rating",value=rr,inline=False)
                    
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
                image = await get_graph(os.environ['USERNAME'], os.environ['PASSWORD'])      
                embed = discord.Embed(
                    title="Test",
                    color = discord.Color.blue()
                )
                embed.set_image(url=f"attachment://graph.png")
                embed.add_field(name="Rank Rating",value="Test Text",inline=False)

                footer = (
                    "🟢 gespielt"
                )
                embed.set_footer(text=footer)

                await ctx.send(file=image, embed=embed)
                       
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

                
    async def get_graph(username, password):
        player_id, headers = val.run(username, password)

        match_data = await val.parse_stats(player_id, headers, 20)
        matches = list(match_data.values())
        ranked_rating = []
        competitive_tier = []

        for match in matches:
            ranked_rating.append(match["ranked_rating"])
            competitive_tier.append(match["competitive_tier"])

        TRR = list(
            reversed(
                [
                    (tier * 100) - 300 + RR
                    for RR, tier in zip(ranked_rating, competitive_tier)
                ]
            )
        )

        x = np.arange(len(TRR))
        y = np.array(TRR)

        segments_x = np.r_[x[0], x[1:-1].repeat(2), x[-1]].reshape(-1, 2)
        segments_y = np.r_[y[0], y[1:-1].repeat(2), y[-1]].reshape(-1, 2)

        # Assign colors to the line segments
        linecolors = ["green" if y_[0] < y_[1] else "red" for y_ in segments_y]

        segments = [list(zip(x_, y_)) for x_, y_ in zip(segments_x, segments_y)]
        min_ = int(math.floor(min(TRR) / 100.0)) * 100
        max_ = int(math.ceil(max(TRR) / 100.0)) * 100
        # Create figure
        plt.figure(figsize=(12, 5), dpi=150)
        plt.style.use("dark_background")
        ax = plt.axes()

        # Add a collection of lines
        ax.add_collection(LineCollection(segments, colors=linecolors))
        ax.scatter(x, y, c=[linecolors[0]] + linecolors, zorder=10)
        ax.set_xlim(0, len(x) - 1)
        ax.set_ylim(min_, max_)

        ax.xaxis.grid(linestyle="dashed")
        ax.yaxis.grid(linestyle="dashed")
        ax.spines["top"].set_linestyle("dashed")
        ax.spines["bottom"].set_capstyle("butt")
        ax.spines["right"].set_linestyle("dashed")
        ax.spines["bottom"].set_capstyle("butt")
        plt.xlabel("Past Matches")
        plt.ylabel("Rank Rating (RR)")
        plt.title("Rank Rating History")
        plt.xticks(np.arange(len(x)), labels=x[::-1])
        plt.yticks(np.arange(min_, max_, 100))
        plt.tight_layout()
        plt.savefig("graph.png", transparent=True)
        plt.close()

        with open("graph.png", "rb") as f:
            file = io.BytesIO(f.read())
        image = discord.File(file, filename="graph.png")

        return image

    
    
def setup(client):
    client.add_cog(graph(client))
    print("Graph      | Imported") 
