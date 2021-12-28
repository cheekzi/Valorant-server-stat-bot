import requests
import re
import discord
import asyncio
from discord.ext import commands
import json 
from .utils.shop_utils import username_to_data,getVersion,priceconvert,skins,check_item_shop
from .utils.profile_utils import loggedInStats, getingamename
from discord_components import *
from datetime import datetime

with open ('././config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    prefix = config['prefix']

class itemshop(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
            
        if not message.author.bot:
            print(message.content)
            if not message.guild:
                
                author_id = str(message.author.id)
                user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
                
                if message.content.startswith('username='):
                    username = message.content.split('=')
                    
                    if not user:
                        await self.client.pg_con.execute("INSERT INTO riotpwd (user_id, username) VALUES ($1, $2)", author_id, username[1])
                        await message.channel.send("Successfully updated your username")
                    else:
                        await self.client.pg_con.execute("UPDATE riotpwd SET username = $1 WHERE user_id = $2",username[1], author_id)
                        await message.channel.send("Successfully updated your username")
                if message.content.startswith('password='):
                    password = message.content.split('=')
                    
                    await self.client.pg_con.execute("UPDATE riotpwd SET password = $1 WHERE user_id = $2",password[1], author_id)
                    await message.channel.send("Successfully updated your password")
                
                if message.content.startswith('region='):
                    region = message.content.split('=')
                    
                    await self.client.pg_con.execute("UPDATE riotpwd SET region = $1 WHERE user_id = $2",region[1], author_id)
                    await message.channel.send("Successfully updated your region")
                
                
                if message.content.startswith('!logout'):
                    await self.client.pg_con.execute("DELETE FROM riotpwd WHERE user_id = $1",author_id)
                    await message.channel.send("Successfully logged you out")
                
                if message.content.startswith('!reglist'):
                    embed = discord.Embed(
                        color= discord.Color.blue()
                    )
                    embed.add_field(name ="REGION LIST",value="""
                        `na` - North America
                        `eu` - Europe
                        `br` - Brazil
                        `ap` - Asia Pacific
                        `kr` - Korea
                        `latam` - Latin America
                    """,inline=False)
                    await message.channel.send(embed=embed)
                    
                msg = await message.channel.history(limit=2).flatten()
                
                dic = None
                msg = msg[1].embeds
                for ms in msg:
                    dic = ms.to_dict()
                
                if dic == None:
                    return
                if dic["fields"][0]["name"] == "Username": 
                    if not user:
                        await self.client.pg_con.execute("INSERT INTO riotpwd (user_id, username) VALUES ($1, $2)", author_id, message.content)

                    else:
                        await self.client.pg_con.execute("UPDATE riotpwd SET username = $1 WHERE user_id = $2",message.content, author_id)

                    await message.channel.send("Successfully updated your username")  
                    dm_embed = discord.Embed(
                        color=discord.Color.red()
                    )
                    dm_embed.add_field(name ="Password",value="Enter your **Password** \n for example `123`",inline=False)
                    await message.channel.send(embed=dm_embed)

                elif dic["fields"][0]["name"] == "Password":
                    await self.client.pg_con.execute("UPDATE riotpwd SET password = $1 WHERE user_id = $2",message.content, author_id)
                    await message.channel.send("Successfully updated your password")

                    dm_embed = discord.Embed(
                        color=discord.Color.red()
                    )
                    dm_embed.add_field(name ="Region",value="Enter your **Region** \n for example `eu`",inline=False)
                    await message.channel.send(embed=dm_embed)

                elif dic["fields"][0]["name"] == "Region":
                    await self.client.pg_con.execute("UPDATE riotpwd SET region = $1 WHERE user_id = $2",message.content, author_id)
                    await message.channel.send("Successfully updated your region")

                    dm_embed = discord.Embed(
                        color=0xA6FF0A
                    )
                    dm_embed.add_field(name="Finished", value="If everything is correct try !shop , !profile , !rank and more.. \n Otherwise you can change any personal information with username=`your_username`, password=`your_password`, region=`your_region`. \n **Loading**", inline=False)
                    await message.channel.send(embed=dm_embed)
                    
                    try:
                        
                        user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
                        username = user['username']
                        password = user['password']
                        region   = user['region']
                        
                        user_data = username_to_data(username, password)
                        user_id = user_data[2]
                        raw_ingame_user = getingamename(region, user_id)

                        ingame_username = raw_ingame_user['data']['name']
                        ingame_tag = raw_ingame_user['data']['tag']
                        player_name = ingame_username+" #" +ingame_tag
                        ranking_in_tier = raw_ingame_user['data']['current_data']['ranking_in_tier']

                        profile = await loggedInStats(ingame_username,ingame_tag)
                        rank = profile["rank"]
                        
                        if user:

                            rr = f"**{ranking_in_tier} / 100** RR\n"

                        embed = discord.Embed(
                            title=rank,
                            timestamp=datetime.utcnow(), 
                            color = 0x02FCCF
                        )
                        embed.set_thumbnail(url=profile["rankIconUrl"])
                        embed.set_author(name=player_name, icon_url=profile["avatarUrl"],url=profile["avatarUrl"])
                        embed.add_field(name="Rank Rating",value=rr,inline=False)

                        footer = (
                            "🟢 Time Played " + str(profile["time_played"]) + " Account-Level " + str(profile["account_level"])
                        )
                        embed.set_footer(text=footer)
                        await message.channel.send(embed=embed)
                        await message.channel.send("**Connected**.")
                        
                    except Exception as e:
                        print(e)                  
                
                
    
    @commands.command()
    async def login(self, ctx):
        embed = discord.Embed(
            color = discord.Color.blue(),
            description = "Check your DM"
        )
        await ctx.send(embed=embed)

        dm_embed = discord.Embed(
            color=0xA6FF0A,
            title="LOGIN PAGE"
        )
 
        dm_embed.add_field(name="NOTE",value ="`Log In` to your Valorant Account in Order to use the Bots Features (Shop, Stats, Rank..)",inline=False)
        dm_embed.add_field(name="Information",value ="Stay logged in for easier access or \n `Log Out` afterwards with **!Logout** \n You can also still change any false information with username=`your_username`, password=`your_password` or region=`your_region` in this Chat afterwards.", inline=False)

        await ctx.author.send(embed=dm_embed)
        
        next_embed = discord.Embed(
            color=discord.Color.red()
        )
        next_embed.add_field(name ="Username",value="Enter your **Username** now \n for example `cheekz`",inline=False)
        await ctx.author.send(embed=next_embed)
        



    @commands.command()
    async def shop(self, ctx):
        author_id = str(ctx.author.id)
        
        try:
            user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
            username = user['username']
            password = user['password']
            region = user['region']
        except:
            embed = discord.Embed(
                color= discord.Color.red()
            )
            embed.add_field(name ="HOLD ON MAN !",value = f"""
            you need to login to your account before you can use this command,
            use `{prefix}login` to login to your account
            """)
            await ctx.send(embed=embed)
        


        try: 
            if user:
                await ctx.send("Loading shop...")
                user_data = username_to_data(username, password)
                access_token = user_data[0]
                entitlements_token = user_data[1]
                user_id = user_data[2]
                skin_data = await skins(entitlements_token, access_token, user_id, region)
                embed = discord.Embed(title=skin_data["bundle_name"], color=0x00FC7E)
                embed.set_image(url=skin_data["bundle_image"])
                await ctx.send(embed=embed)
                try:
                    embed = discord.Embed(title=f"{skin_data['skin1_name']} costs {skin_data['skin1_price']}", color=0x00FC7E)
                    embed.set_image(url=skin_data["skin1_image"])
                    await ctx.send(embed=embed)
                    embed = discord.Embed(title=f"{skin_data['skin2_name']} costs {skin_data['skin2_price']}", color=0x00FC7E)
                    embed.set_image(url=skin_data["skin2_image"])
                    await ctx.send(embed=embed)
                    embed = discord.Embed(title=f"{skin_data['skin3_name']} costs {skin_data['skin3_price']}", color=0x00FC7E)
                    embed.set_image(url=skin_data["skin3_image"])
                    await ctx.send(embed=embed)
                    embed = discord.Embed(title=f"{skin_data['skin4_name']} costs {skin_data['skin4_price']}", color=0x00FC7E)
                    embed.set_image(url=skin_data["skin4_image"])
                    embed.set_footer(text=(f"Time Remaining : "+ str(skin_data['SingleItemOffersRemainingDurationInSeconds']) + skin_data['time_units']))
                    await ctx.send(embed=embed)
                    
                
                except:
                    jkbkj
                    await ctx.send("Loading complete!")
                    pass
        except Exception as e:
            kjafa();
            print(e)
            embed= discord.Embed(
                color=discord.Color.red()
            )
            embed.add_field(name ="SOME ERROR OCCURED...",value="""
            Either your `username` \nor your `password` \nor your `region` is incorrect.
            """,inline=False)
            embed.set_thumbnail(url="https://i.imgur.com/A45DVhf.gif")
            await ctx.send(
                embed=embed
            )







def setup(client):
    client.add_cog(itemshop(client))
    print("itemshop     | Imported")
