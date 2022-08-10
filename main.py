import discord
import os
import json
import random
import keep_alive
import asyncio
import time

from discord import Intents
from discord.ui import Button, View
from discord.ext import commands
from discord.ext.commands import slash_command

intents = Intents.all()

token = os.environ['TOKEN']

def mixedCase(*args):
  total = []
  import itertools
  for string in args:
    a = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in       string)))
    for x in list(a): total.append(x)

  return list(total)

async def give_xp(user):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(user.id) in data:
    xp = (data[str(user.id)]["rebirth"] + 1 * 5) + random.randint(100, 250)

    data[str(user.id)]["xp"] += xp

    with open("data.json", "w") as file:
      json.dump(data, file, indent=3)
  else:
    return False

async def level_system(user, base):
    with open("data.json", "r") as file:
      data = json.load(file)
      
    if str(user.id) in data:
      user_xp = data[str(user.id)]["xp"]
      max_xp = data[str(user.id)]["maxxp"]
      if user_xp >= max_xp:
        data[str(user.id)]["level"] += 1
        data[str(user.id)]["xp"] -= user_xp
        data[str(user.id)]["maxxp"] += 1000

        with open("data.json", "w") as file:
          json.dump(data, file, indent=3)

        embed = discord.Embed(title="Level Up", description="Please use d!bal to check your level and xp", color=discord.Color.dark_teal())

        await base.send(embed=embed, delete_after=10)

client = commands.Bot(command_prefix=mixedCase("d!"), intents=intents, status=discord.Status.idle, activity=discord.Game("/help | d!help"), case_insensitive=True)

dev_id = 763950497781514300

@client.event
async def on_ready():
    print("Dxrie Assistant is ready")

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.BadArgument):
    embed = discord.Embed(title="Error", description="Invalid Argument Please Type in The Correct Argument. (d!help {command_name} for more information about command argument)", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)
  elif isinstance(error, commands.MissingRequiredArgument):
    embed = discord.Embed(title="Error", description="Missing Required Argument Please Type in The Required Argument. (d!help {command_name} for more information about command argument)", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)
  elif isinstance(error, commands.MissingPermissions):
    embed = discord.Embed(title="Error", description="Missing Required Permission Please Contact The Server's Administrator For More Information.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)
  elif isinstance(error, commands.CommandOnCooldown):
    embed = discord.Embed(title="Error", description=f"This command is on {error.retry_after:.2f}s cooldown", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)
  elif isinstance(error, commands.CommandNotFound):
    embed = discord.Embed(title="Error", description="Command isn't found, might wanna check with slash command?", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.event
async def on_message(message):
  if message.author.id == client.user.id:
    return
  if message.content.lower().startswith("d!"):
    await level_system(user=message.author, base=message.channel)
    await client.process_commands(message)
  else:
    await level_system(user=message.author, base=message.channel)

@client.slash_command(name="ping", description="Check the bot's latency/ping")
async def ping(ctx):
    embed = discord.Embed(title="Ping", description=f"{round(client.latency * 1000)} ms", color=discord.Color.green())

    await ctx.respond(embed=embed)

@client.slash_command(name="clear", description="Mass clear message in discord channel.")
async def clear(ctx, limit : int):
    if ctx.author.guild_permissions.manage_messages or ctx.author.id == dev_id:
        await ctx.channel.purge(limit=limit)

        embed = discord.Embed(title="Cleared", description=f"{limit} messages", color=discord.Color.dark_gold())

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Error", description=f"Missing required permission please contact the server's administrator", color=discord.Color.red())

        await ctx.respond(embed=embed, delete_after=10)

@client.slash_command(name="start", description="Start your journey and register with this command.")
async def start(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    embed = discord.Embed(title="Your account is already registered you can only create 1 account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed)
  else:
    data[str(ctx.author.id)] = {}
    data[str(ctx.author.id)]["wallet"] = 0
    data[str(ctx.author.id)]["bank"] = 0
    data[str(ctx.author.id)]["rebirth"] = 0
    data[str(ctx.author.id)]["gems"] = 0
    data[str(ctx.author.id)]["crate"] = 0
    data[str(ctx.author.id)]["farm"] = 1
    data[str(ctx.author.id)]["xp"] = 0
    data[str(ctx.author.id)]["maxxp"] = 1000
    data[str(ctx.author.id)]["coins"] = 2500
    data[str(ctx.author.id)]["level"] = 1
    data[str(ctx.author.id)]["rare_egg"] = 0
    data[str(ctx.author.id)]["common_egg"] = 0
    data[str(ctx.author.id)]["legend_egg"] = 0
    data[str(ctx.author.id)]["title"] = {}
    data[str(ctx.author.id)]["title"]["equipped"] = "Beginner"

    with open("data.json", "w") as file:
      json.dump(data, file, indent=3)

    embed = discord.Embed(title="Account Created", description="You can now interact and use our economy system.", color=discord.Color.teal())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed)

@client.command(name="isdev", help="Check if someone is the developer of this bot.")
async def isdev(ctx, developer : discord.Member):
  with open("developer.json", "r") as file:
    data = json.load(file)

  if str(developer.id) in data:
    await ctx.author.send(f"{developer} is a developer")
  else:
    await ctx.author.send(f"{developer} is not a developer")

@client.command(aliases=["balance", "coin", "coins"], help="Check your account details with this command.")
async def bal(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    wallet = data[str(ctx.author.id)]["wallet"]
    bank = data[str(ctx.author.id)]["bank"]
    rebirth = data[str(ctx.author.id)]["rebirth"]
    gems = data[str(ctx.author.id)]["gems"]
    crate = data[str(ctx.author.id)]["crate"]
    farm = data[str(ctx.author.id)]["farm"]
    level = data[str(ctx.author.id)]["level"]
    xp = data[str(ctx.author.id)]["xp"]
    max = data[str(ctx.author.id)]["maxxp"]
    title = data[str(ctx.author.id)]["title"]["equipped"]

    embed = discord.Embed(title=f":gear: ┇ {title}", color=discord.Color.gold())
    embed.add_field(name="Account Details", value=f"""

                    
                    Wallet : {wallet} :coin:
                    
                    Bank : {bank} :coin:
                    
                    Rebirth : {rebirth}
                    
                    Farm : {farm}
                    
                    Gems : {gems} :gem:
                    
                    Crate : {crate}
                    
                    Level : {level}
                    
                    XP : {xp} / {max}
                    """,
                    inline=False)
    embed.set_footer(icon_url=ctx.author.avatar, text=f"{ctx.author} | {title}")

    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.command(aliases=["depo", "dep"], help="Deposit your coins from your wallet to the bank.")
async def deposit(ctx, amount):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    try:
      amount = int(amount)
    except ValueError:
      amount = str(amount)
      
    if type(amount) == str:
      if amount.lower() == "all":
        if data[str(ctx.author.id)]["wallet"] != 0:
          wallet = data[str(ctx.author.id)]["wallet"]
        
          data[str(ctx.author.id)]["wallet"] -= wallet
          data[str(ctx.author.id)]["bank"] += wallet

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title=f"Successfully Deposited {wallet} :coin: to The Bank", description="You Can Use d!withdraw to withdraw your coins.", color=discord.Color.dark_gold())
          embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

          await ctx.send(embed=embed)
        else:
          embed = discord.Embed(title="Your Wallet Balance is 0", description="Please try again later", color=discord.Color.red())
          embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

          await ctx.send(embed=embed)
      else:
        raise commands.BadArgument
    else:
      if amount <= data[str(ctx.author.id)]["wallet"]:
        if amount > 0:
          data[str(ctx.author.id)]["wallet"] -= amount
          data[str(ctx.author.id)]["bank"] += amount

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title=f"Successfully Deposited {amount} :coin: to The Bank", description="You Can Use d!withdraw to withdraw your coins.", color=discord.Color.dark_gold())
          embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

          await ctx.send(embed=embed)
        else:
          raise commands.BadArgument
      else:
        wallet = data[str(ctx.author.id)]["wallet"]
        
        embed = discord.Embed(title=f"You Can't Deposit More Than Your Wallet Balance, Your Wallet Balance is {wallet} :coin:", description=f"Please choose a lower value", color=discord.Color.red())
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.command(aliases=["wd"], help="Withdraw your coins from the bank to your wallet.")
async def withdraw(ctx, amount):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    try:
      amount = int(amount)
    except ValueError:
      amount = str(amount)
      
    if type(amount) == str:
      if amount.lower() == "all":
        if data[str(ctx.author.id)]["bank"] != 0:
          bank = data[str(ctx.author.id)]["bank"]
        
          data[str(ctx.author.id)]["wallet"] += bank
          data[str(ctx.author.id)]["bank"] -= bank

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title=f"Successfully Withdrawn {bank} :coin: to Your Wallet", description="You Can Use d!deposit to deposit your coins.", color=discord.Color.dark_gold())
          embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

          await ctx.send(embed=embed)
        else:
          embed = discord.Embed(title="Your Wallet Balance is 0", description="Please try again later", color=discord.Color.red())
          embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

          await ctx.send(embed=embed)
      else:
        raise commands.BadArgument
    else:
      if amount <= data[str(ctx.author.id)]["bank"]:
        if amount > 0:
          data[str(ctx.author.id)]["bank"] -= amount
          data[str(ctx.author.id)]["wallet"] +=  amount

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title=f"Successfully Withdrawn {amount} :coin: to Your Wallet", description="You Can Use d!deposit to deposit your coins.", color=discord.Color.dark_gold())
          embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

          await ctx.send(embed=embed)
        else:
          raise commands.BadArgument
      else:
        bank = data[str(ctx.author.id)]["bank"]
        
        embed = discord.Embed(title=f"You Can't Withdraw More Than Your Bank Balance, Your Bank Balance is {bank} :coin:", description=f"Please choose a lower value", color=discord.Color.red())
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

        await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.command(aliases=["h"], help="Hunt monsters and earn money with this command")
@commands.cooldown(3, 60, commands.BucketType.user)
async def hunt(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    monster_legend = ["The Grim", "The Leviathan", "The Dark Matter Entitiy", "The Warden", "The Spiritblood"]
    monster_mythic = ["404 Entity", "The Banshee", "Amarok Entity", "The Camazotz", "Erymanthian Boar", "Dormamu", "The Kluddle"]
    monster_rare = ["Stonefang", "Soulspirit", "Cloudstrike", "Sleipnir", "Enderfox", "Cloudfear", "Spirit Dog"]
    monster_common = ["Sea Dragon", "Netherkeeper", "Gravekeeper", "Skeleton", "Golem", "Slime"]
    pili = ["mitik", "lejen", "rare", "common", "common", "common", "common", "common", "rare", "rare", "rare", "rare", "lejen", "lejen", "common", "common", "common", "common", "common", "rare", "rare", "rare", "common", "common", "common", "common", "rare", "common", "common"]
    rebirth = data[str(ctx.author.id)]["rebirth"] + 1

    legend = random.choice(monster_legend)
    mythic = random.choice(monster_mythic)
    rare = random.choice(monster_rare)
    common = random.choice(monster_common)
    pick = random.choice(pili)

    if pick.lower() == "mitik":
      mythic_earn = random.randint(3000, 5000) * rebirth
      
      embed = discord.Embed(title=f"You Have Caught {mythic}")
      embed.add_field(name="Rarity", value="`Mythical`")
      embed.add_field(name="Earning", value=f"{mythic_earn} :coin:")
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.send(embed=embed)

      data[str(ctx.author.id)]["wallet"] += mythic_earn

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      await give_xp(ctx.author)
    elif pick.lower() == "lejen":
      if "gsc" in data[str(ctx.author.id)]:
        legend_earn = random.randint(1000, 2000) * rebirth
      
        embed = discord.Embed(title=f"You Have Caught {legend}", color=discord.Color.dark_teal())
        embed.add_field(name="Rarity", value="`Legendary`")
        embed.add_field(name="Earning", value=f"{legend_earn} :coin:\n100 :gem:")
        embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

        await ctx.send(embed=embed)
        
        data[str(ctx.author.id)]["wallet"] += legend_earn
        data[str(ctx.author.id)]["gems"] += 100

        with open("data.json", "w") as file:
          json.dump(data, file, indent=3)

        await give_xp(ctx.author)
      else:
        legend_earn = random.randint(1000, 2000) * rebirth
      
        embed = discord.Embed(title=f"You Have Caught {legend}", color=discord.Color.dark_teal())
        embed.add_field(name="Rarity", value="`Legendary`")
        embed.add_field(name="Earning", value=f"{legend_earn} :coin:")
        embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

        await ctx.send(embed=embed)
        
        data[str(ctx.author.id)]["wallet"] += legend_earn

        with open("data.json", "w") as file:
          json.dump(data, file, indent=3)

        await give_xp(ctx.author)
    elif pick.lower() == "rare":
      rare_earn = random.randint(150, 400) * rebirth
      
      embed = discord.Embed(title=f"You Have Caught {rare}", color=discord.Color.gold())
      embed.add_field(name="Rarity", value="`Rare`")
      embed.add_field(name="Earning", value=f"{rare_earn} :coin:")
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.send(embed=embed)

      data[str(ctx.author.id)]["wallet"] += rare_earn

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      await give_xp(ctx.author)
        
    elif pick.lower() == "common":
      common_earn = random.randint(80, 150) * rebirth
      
      embed = discord.Embed(title=f"You Have Caught {common}", color=discord.Color.blurple())
      embed.add_field(name="Rarity", value="`Common`")
      embed.add_field(name="Earning", value=f"{common_earn} :coin:")
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.send(embed=embed)

      data[str(ctx.author.id)]["wallet"] += common_earn

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      await give_xp(ctx.author)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.command(aliases=["d"], help="Claim your daily rewards (24 hours cooldown)")
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    rebirth = data[str(ctx.author.id)]["rebirth"] + 1
    earning = random.randint(250, 500) * rebirth
    crate = random.randint(1, 3)

    data[str(ctx.author.id)]["wallet"] += earning
    data[str(ctx.author.id)]["crate"] += crate

    with open("data.json", "w") as file:
      json.dump(data, file, indent=3)

    embed = discord.Embed(title="Daily Rewards", color=discord.Color.dark_gold())
    embed.add_field(name="Rewards", value=f"Earned {earning} :coin: and {crate} crate")
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed)
    await give_xp(ctx.author)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.command(name="crate", help="Unbox crate and earn coins to help you rebirth")
async def crate(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    crate = data[str(ctx.author.id)]["crate"]
    rebirth = data[str(ctx.author.id)]["rebirth"] + 1

    if crate != 0:
      earning = random.randint(50, 100) * rebirth
      
      data[str(ctx.author.id)]["crate"] -= 1
      data[str(ctx.author.id)]["wallet"] += earning

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      embed = discord.Embed(title="Crate", description=f"Earned {earning} :coin:", color=discord.Color.dark_gold())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)
      
      await ctx.send(embed=embed)
    else:
      embed = discord.Embed(title="You ran out of crates", description="Please use d!daily to claim your crates", color=discord.Color.red())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.slash_command(aliases=["reb"], description="Rebirth and earn a boost to help you start a new fresh and fun journey")
async def rebirth(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  earning = random.randint(100, 250)

  xp = random.randint(50, 100)
  
  if str(ctx.author.id) in data:
    price = data[str(ctx.author.id)]["coins"]
    if "cheapreb" in data[str(ctx.author.id)]:
      if data[str(ctx.author.id)]["cheapreb"] == 1:
        if data[str(ctx.author.id)]["bank"] >= price * 0.25:
          data[str(ctx.author.id)]["rebirth"] += 1
          data[str(ctx.author.id)]["bank"] = 0
          data[str(ctx.author.id)]["wallet"] = 0
          data[str(ctx.author.id)]["gems"] += earning
          data[str(ctx.author.id)]["coins"] += 2500
          data[str(ctx.author.id)]["xp"] += xp

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title="Successfully Rebirthed", description=f"Your bank balance has been set to 0 and you received {earning} gems.")
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)
          await ctx.respond(embed=embed)
        else:
          embed = discord.Embed(title=f"You need atleast {round(price * 0.25)} :coin: in your bank", description="Please try again later", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.send(embed=embed, delete_after=10)
      elif data[str(ctx.author.id)]["cheapreb"] == 2:
        if data[str(ctx.author.id)]["bank"] >= price * 0.35:
          data[str(ctx.author.id)]["rebirth"] += 1
          data[str(ctx.author.id)]["bank"] = 0
          data[str(ctx.author.id)]["wallet"] = 0
          data[str(ctx.author.id)]["gems"] += earning
          data[str(ctx.author.id)]["coins"] += 2500
          data[str(ctx.author.id)]["xp"] += xp

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title="Successfully Rebirthed", description=f"Your bank balance has been set to 0 and you received {earning} gems.")
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)
          await ctx.respond(embed=embed)
        else:
          embed = discord.Embed(title=f"You need atleast {round(price * 0.35)} :coin: in your bank", description="Please try again later", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.send(embed=embed, delete_after=10)
      elif data[str(ctx.author.id)]["cheapreb"] == 3:
        if data[str(ctx.author.id)]["bank"] >= price * 0.45:
          data[str(ctx.author.id)]["rebirth"] += 1
          data[str(ctx.author.id)]["bank"] = 0
          data[str(ctx.author.id)]["wallet"] = 0
          data[str(ctx.author.id)]["gems"] += earning
          data[str(ctx.author.id)]["coins"] += 2500
          data[str(ctx.author.id)]["xp"] += xp

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title="Successfully Rebirthed", description=f"Your bank balance has been set to 0 and you received {earning} gems.")
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)
          await ctx.respond(embed=embed)
        else:
          embed = discord.Embed(title=f"You need atleast {round(price * 0.45)} :coin: in your bank", description="Please try again later", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed, delete_after=10)
    else:
      if data[str(ctx.author.id)]["bank"] >= price:
          data[str(ctx.author.id)]["rebirth"] += 1
          data[str(ctx.author.id)]["bank"] = 0
          data[str(ctx.author.id)]["wallet"] = 0
          data[str(ctx.author.id)]["coins"] += 2500
          data[str(ctx.author.id)]["gems"] += earning
          data[str(ctx.author.id)]["xp"] += xp

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title="Successfully Rebirthed", description=f"Your bank balance has been set to 0 and you received {earning} gems.")
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)
          await ctx.respond(embed=embed)
      else:
          embed = discord.Embed(title=f"You need atleast {price} :coin: in your bank", description="Please try again later", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed, delete_after=10)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed, delete_after=10)

@client.command(aliases=["f"], help="Be a farmer and earn coins to help you rebirth.")
@commands.cooldown(1, 30, commands.BucketType.user)
async def farm(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    rebirth = data[str(ctx.author.id)]["rebirth"] + 1
    level = data[str(ctx.author.id)]["farm"]
    earning = random.randint(1500, 5000) + (rebirth * 20) + (level * 500)
    
    data[str(ctx.author.id)]["wallet"] += earning

    with open("data.json", "w") as file:
      json.dump(data, file, indent=3)

    embed = discord.Embed(title="Farming", description=f"Earned {earning} coins from farming", color=discord.Color.teal())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed)
    await give_xp(ctx.author)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.slash_command(name="upgradefarm", description="Upgrade your farm level and earn more money.")
async def upgradefarm(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    price = data[str(ctx.author.id)]["farm"] * 100
    gems = data[str(ctx.author.id)]["gems"]
    if data[str(ctx.author.id)]["gems"] >= price:
      data[str(ctx.author.id)]["farm"] += 1
      data[str(ctx.author.id)]["gems"] -= price

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      level = data[str(ctx.author.id)]["farm"]

      embed = discord.Embed(title="Increased Farm Level", description=f"Current Level : {level}", color=discord.Color.dark_teal())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.respond(embed=embed)
    else:
      embed = discord.Embed(title="Insufficient Gems", description=f"You are {gems - price} :gem: short.", color=discord.Color.red())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.respond(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed, delete_after=10)

@client.command(name="guess", help="Guess the correct number between 1-10 and earn from 2000 to 5000 coins. (3 chance)")
@commands.cooldown(3, 3600, commands.BucketType.user)
async def guess(ctx, number : int):
  with open("data.json", "r") as file:
    data = json.load(file)

  number2 = random.randint(1, 10)
  earning = random.randint(2000, 5000)
  
  if str(ctx.author.id) in data:
    if number <= 10:
      if number != 0:
        if number == number2:
          embed = discord.Embed(title=f"Earned {earning} :coin: from guessing the correct number", color=discord.Color.dark_gold())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.send(embed=embed)
        else:
          embed = discord.Embed(title="Invalid Guess Please Try Again", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.send(embed=embed, delete_after=10)
      else:
        raise commands.BadArgument
    else:
      raise commands.BadArgument
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed, delete_after=10)

@client.slash_command(name="catalog", description="Check the list of available items through this command")
async def catalog(ctx):
  await ctx.respond("https://dxrieassistant.dxrie.repl.co/shop.html")

@client.slash_command(name="buy", description="/buy {item_id} to buy an item listed in /catalog")
async def buy(ctx, id : str):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    gems = data[str(ctx.author.id)]["gems"]
    if id.lower() == "cheapreb":
      if "cheapreb" in data[str(ctx.author.id)]:
        if data[str(ctx.author.id)]["cheapreb"] == 1:
          if data[str(ctx.author.id)]["gems"] >= 500:
            data[str(ctx.author.id)]["cheapreb"] += 1
            data[str(ctx.author.id)]["gems"] -= 500

            with open("data.json", "w") as file:
              json.dump(data, file, indent=3)
          else:
            embed = discord.Embed(title="Insufficient Gems", description=f"You are {gems - 500} :gem: short to upgrade cheap rebirth.", color=discord.Color.red())
            embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

            await ctx.respond(embed=embed)
        elif data[str(ctx.author.id)]["cheapreb"] == 2:
          if data[str(ctx.author.id)]["gems"] >= 1000:
            data[str(ctx.author.id)]["cheapreb"] += 1
            data[str(ctx.author.id)]["gems"] -= 1000

            with open("data.json", "w") as file:
              json.dump(data, file, indent=3)
          else:
            embed = discord.Embed(title="Insufficient Gems", description=f"You are {gems - 1000} :gem: short to upgrade cheap rebirth.", color=discord.Color.red())
            embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

            await ctx.respond(embed=embed)
        elif data[str(ctx.author.id)]["cheapreb"] == 3:
          embed = discord.Embed(title="Maximum Cheap Rebirth Level", description="You can't upgrade cheap rebirth more than 3 times.", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed, delete_after=10)
      else:
        if data[str(ctx.author.id)]["gems"] >= 250:
            data[str(ctx.author.id)]["cheapreb"] = 1
            data[str(ctx.author.id)]["gems"] -= 250

            with open("data.json", "w") as file:
              json.dump(data, file, indent=3)
        else:
            embed = discord.Embed(title="Insufficient Gems", description=f"You are {gems - 250} :gem: short to upgrade cheap rebirth.", color=discord.Color.red())
            embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

            await ctx.respond(embed=embed)
    elif id.lower() == "gsc":
      if "gsc" in data[str(ctx.author.id)]:
        embed = discord.Embed(title="The Grim Scythe isn't upgradable", description="Please choose another item beside The Grim Scythe since you already owned it.", color=discord.Color.red())
        embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

        await ctx.respond(embed=embed, delete_after=10)
      else:
        if gems >= 1000:
          data[str(ctx.author.id)]["gsc"] = True
          data[str(ctx.author.id)]["gems"] -= 1000

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title="Successfully Bought The Grim Scythe", description="Item ID : gsc", color=discord.Color.default())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed)
        else:
          embed = discord.Embed(title="Insufficient Gems", description=f"You are {gems - 1000} :gem: short to purchase The Grim Scythe.", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed)
    elif id.lower() == "lucky":
      if "lucky" in data[str(ctx.author.id)]:
        embed = discord.Embed(title="Lucky Enhancer isn't upgradable", description="Please choose another item beside Lucky Enhancer since you already owned it.", color=discord.Color.red())
        embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

        await ctx.respond(embed=embed, delete_after=10)
      else:
        if gems >= 300:
          data[str(ctx.author.id)]["lucky"] = True
          data[str(ctx.author.id)]["gems"] -= 300

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title="Successfully Bought Lucky Enhancer", description="Item ID : lucky", color=discord.Color.default())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed)
        else:
          embed = discord.Embed(title="Insufficient Gems", description=f"You are {gems - 300} :gem: short to purchase Lucky Enhancer.", color=discord.Color.red())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed)
    else:
      await ctx.respond("Please use /catalog to check available items.", ephemeral=True)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed, delete_after=10)

@client.command(aliases=["chest", "tc", "treasurechest"], help="Be a pirate and claim coins from treasure chest")
@commands.cooldown(1, 7200, commands.BucketType.user)
async def treasure(ctx):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    if "lucky" in data[str(ctx.author.id)]:
      rebirth = data[str(ctx.author.id)]["rebirth"] + 1
      earning = random.randint(100, 200) * rebirth
      earngems = random.randint(20, 50)
      
      data[str(ctx.author.id)]["gems"] += earngems
      data[str(ctx.author.id)]["wallet"] += earning

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      embed = discord.Embed(title="Treasure Chest", description=f"Earned {earning} :coin: and {earngems} :gem: from the treasure chest.")
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.send(embed=embed)
    else:
      rebirth = data[str(ctx.author.id)]["rebirth"] + 1
      earning = random.randint(100, 200) * rebirth
      
      data[str(ctx.author.id)]["wallet"] += earning

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      embed = discord.Embed(title="Treasure Chest", description=f"Earned {earning} :coin: from the treasure chest.")
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.command(aliases=["tl"], help="Check for any available title")
async def titlelist(ctx):
  title = """
  ```
  1. Beginner (Level 1) id:1
  2. Newbie (Level 5) id:5
  3. Intermediate (Level 10) id:10
  4. Prime (Level 13) id:13
  5. No Lifer (Level 15) id:15
  6. Immortal (Level 20) id:20
  7. Supreme (Level 30) id:30
  8. Lucky (Level 35) id:35
  9. Avatar (Level 50) id:50
  10. Mercenary (Level 55) id:55
  11. Overlord (Level 70) id:70
  12. 24/7 (Level 100) id:100
  ```
  """

  await ctx.author.send(title)

@client.slash_command(name="title", description="Equip a title based on your level.")
async def title(ctx, title_id : int):
  with open("data.json", "r") as file:
    data = json.load(file)

  with open("title.json", "r") as file:
    title = json.load(file)

  title = title[str(title_id)]

  if str(ctx.author.id) in data:
    if "title" in data[str(ctx.author.id)]:
      if title_id <= data[str(ctx.author.id)]["level"]:
        if title_id == 1:
          data[str(ctx.author.id)]["title"]["equipped"] = "Beginner"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 5:
          data[str(ctx.author.id)]["title"]["equipped"] = "Newbie"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 10:
          data[str(ctx.author.id)]["title"]["equipped"] = "Intermediate"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 15:
          data[str(ctx.author.id)]["title"]["equipped"] = "No Lifer"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 20:
          data[str(ctx.author.id)]["title"]["equipped"] = "Immortal"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 30:
          data[str(ctx.author.id)]["title"]["equipped"] = "Supreme"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id ==35:
          data[str(ctx.author.id)]["title"]["equipped"] = "Lucky"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 50:
          data[str(ctx.author.id)]["title"]["equipped"] = "Avatar"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 25:
          data[str(ctx.author.id)]["title"]["equipped"] = "Beta"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 55:
          data[str(ctx.author.id)]["title"]["equipped"] = "Mercenary"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 70:
          data[str(ctx.author.id)]["title"]["equipped"] = "Overlord"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 13:
          data[str(ctx.author.id)]["title"]["equipped"] = "Prime"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        elif title_id == 100:
          data[str(ctx.author.id)]["title"]["equipped"] = "24/7"

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          await ctx.respond("Equipped", ephemeral=True)
        else:
          await ctx.respond("Unknown Title", ephemeral=True)
      else:
        await ctx.respond("You need a higher level", ephemeral=True)
    else:
      data[str(ctx.author.id)]["title"] = {}
      data[str(ctx.author.id)]["title"]["equipped"] = "Beginner"

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      await ctx.send("Please re-use the command")
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.slash_command(name="buyxp", description="Buy xp and earn fast level to get yourself a title.")
async def buyxp(ctx, xp : int):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    if data[str(ctx.author.id)]["wallet"] >= xp * 10:
      data[str(ctx.author.id)]["wallet"] -= xp * 10
      data[str(ctx.author.id)]["xp"] += xp

      with open("data.json", "w") as file:
        json.dump(data, file, indent=3)

      embed = discord.Embed(title=f"Successfully bought {xp} XP", description=f"-{xp * 10} :coin:", color=discord.Color.blurple())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.respond(embed=embed)
    else:
      wallet = data[str(ctx.author.id)]["wallet"]
      
      embed = discord.Embed(title="Insufficient Coins", description=f"You are {wallet - xp * 10} :coin: short to purchase {xp} XP.", color=discord.Color.red())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.respond(embed=embed)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.send(embed=embed, delete_after=10)

@client.slash_command(name="pay", description="Pay someone with this command")
async def pay(ctx, member : discord.Member, amount : int):
  with open("data.json", "r") as file:
    data = json.load(file)

  if str(ctx.author.id) in data:
    wallet = data[str(ctx.author.id)]["wallet"]
    if str(member.id) in data:
      if amount <= data[str(ctx.author.id)]["wallet"]:
        if amount != 0:
          data[str(ctx.author.id)]["wallet"] -= amount
          data[str(member.id)]["wallet"] += amount

          with open("data.json", "w") as file:
            json.dump(data, file, indent=3)

          embed = discord.Embed(title=f"Successfully paid {member} {amount} :coin:", color=discord.Color.dark_gold())
          embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

          await ctx.respond(embed=embed)
        else:
          raise commands.BadArgument
      else:
        embed = discord.Embed(title=f"Insufficient Coins", description=f"Your wallet balance is {wallet} :coin:", color=discord.Color.red())
        embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

        await ctx.respond(embed=embed, delete_after=10)
    else:
      embed = discord.Embed(title=f"{member} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
      embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

      await ctx.respond(embed=embed, delete_after=10)
  else:
    embed = discord.Embed(title=f"{ctx.author} is Not Registered", description="Please use /start to register your account.", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar, text=ctx.author)

    await ctx.respond(embed=embed, delete_after=10)

keep_alive.keep_alive()
client.run(token)