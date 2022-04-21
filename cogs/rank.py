import discord
from discord.ext import commands
import requests
import json 
from .utils.rank_utils import username_to_data,getrank, getrank_name
from discord_components import *

with open ('././config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    prefix = config['prefix']

class rank(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def rank(self, ctx, *, name=None):
        author_id = str(ctx.author.id)
            
        if not name:
            try:
                user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
                username = user['username']
                password = user['password']
                region = user['region']
                try: 
                    if user:
                        await ctx.send("Loading rank...")
                        user_data = username_to_data(username, password)
                        user_id = user_data[2]
                        #user_id = "2382ed0b-9835-56b0-91c0-cc159d65905d"
                        rank = getrank(region, user_id, user_data[0], user_data[1])
                        print(rank)

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
                        embed = discord.Embed(
                            color=0xFF9B0A,
                            title=dic[rank[0][0]]
                        )
                        embed.add_field(name ="Ranking in Tier",value=f"{rank[0][1]}",inline=True)
                        embed.add_field(name="Peak Rank", value=f"{dic[rank[1]]}", inline=False)
                        embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{rank[0][0]}.png")

                        await ctx.send(embed=embed)

                except Exception as e:
                    print(e)
                    embed= discord.Embed(
                        color=discord.Color.red()
                    )
                    embed.add_field(name ="SOME ERROR OCCURED...",value="""
                    Either your `username` \nor your `password` \nor your `region` is incorrect.
                    """,inline=False)

                    embed.set_thumbnail(url="https://i.imgur.com/A45DVhf.gif")
                    await ctx.send(
                        embed=embed,
                        components=[
                            [
                                Button(label="Support Server", style=5, url="https://discord.gg/m5mSyTV7RR"),
                                Button(label="Vote", style=5, url="https://top.gg/bot/864451929346539530/vote")
                            ]
                        ]
                    )

            except:
                embed = discord.Embed(
                    color= discord.Color.red()
                )
                embed.add_field(name ="HOLD ON MAN !",value = f"""
                you need to login to your account before you can use this command,
                use `{prefix}login` to login to your account
                """)
                await ctx.send(embed=embed)
        else:
            try:
                username = name.split('#')           
                current_rank = getrank_name(username[0], username[1])
                
                player_rank = current_rank['data']['currenttierpatched']
                current_tier = current_rank['data']['currenttier']
                ranking_in_tier = current_rank['data']['ranking_in_tier']
                mmr_change_to_last_game = current_rank['data']['mmr_change_to_last_game']

                embed = discord.Embed(
                    color=0xFF9B0A,
                    title="RANK"
                )
                embed.add_field(name ="Current Rank",value=f"{player_rank}",inline=False)
                embed.add_field(name ="Ranking in Tier",value=f"{ranking_in_tier}",inline=True)
                embed.add_field(name ="Last MMR Change",value=f"{mmr_change_to_last_game}",inline=True)
                embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{current_tier}.png")

                await ctx.send(embed=embed)
                       
            except Exception as e:
                print(e)
                embed= discord.Embed(
                    color=discord.Color.red()
                )
                embed.add_field(name ="SOME ERROR OCCURED...",value=f"""
                Couldn't find statistics for `{name}` \n Check if the name is correct and the player had played rank before this season and try again later.
                """,inline=False)
                embed.set_thumbnail(url="https://i.imgur.com/A45DVhf.gif")
                await ctx.send(
                    embed=embed
                )

def setup(client):
    client.add_cog(rank(client))
    print("rank         | Imported")   
