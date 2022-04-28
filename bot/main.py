import os
import discord

import datetime
import pytz
import random

from keep_alive import keep_alive 

from discord.ext import commands   # Import the discord.py extension "commands"
import discord_slash 
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.utils import manage_commands

#from keep_alive import keep_alive
from replit import db


client = discord.Client()
guild_ids = [925596879008436266]
client = commands.Bot(command_prefix = "!") #unused because of slashes
slash = SlashCommand(client, sync_commands=True)


serve_word = ["bored", "dont know", "sad"]


  
now = datetime.datetime.utcnow()
then = datetime.datetime.utcnow()

#############################################################################################

#db handlers

#triggers
def update_trigger(new_trigger):
  if "triggers" in db.keys():
    triggerdb = db["triggers"]
    triggerdb.append(new_trigger)
    db["triggers"] = triggerdb
  else:
    db["triggers"] = [new_trigger]

def delete_trigger(index):
  triggerdb = db["triggers"]
  if len(triggerdb) > index:
    del triggerdb[index]
  db["triggers"] = triggerdb
  
#orders
def update_order(new_order):
  if "orders" in db.keys():
    orderdb = db["orders"]
    orderdb.append(new_order)
    db["orders"] = orderdb
  else:
    db["orders"] = [new_order]

def delete_order(index):
  orderdb = db["orders"]
  if len(orderdb) > index:
    del orderdb[index]
  db["orders"] = orderdb


  ###################################################################
  #startup sequence




@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game(name='Looking for a victim')) #Bot status, change this to anything you like
  print("Bot online") 


  ###################################################################
#slash integration

@slash.slash(name="clock", description="Displays a local time", guild_ids=guild_ids)
async def _clock(ctx: SlashContext):
  tz = pytz.timezone('America/Toronto')
  utc_now = datetime.datetime.utcnow()
  tz_now = utc_now.astimezone(tz).strftime('%D, %H:%M:%S')

      #sends curent adjusted time
  await ctx.send(content ='time is ' + str(tz_now))

@slash.slash(name="set", description="saves the current time", guild_ids=guild_ids)
async def _set(ctx: SlashContext):
  
  use_store = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
  db["uses"] = use_store
  
  #send a confirmation bot saved
  await ctx.send(content = 'time saved') 
  
@slash.slash(name="since", description="Displays the time that has passed",  guild_ids=guild_ids)
async def _since(ctx: SlashContext):

  use_time = datetime.datetime.strptime(db["uses"], "%d-%b-%Y (%H:%M:%S)")
  now = datetime.datetime.now() #get current time

  duration = now - use_time #figure out difference since stored to now in datecodes
  duration_in_s = duration.total_seconds() #convert result to lowest used value for display

      #does math magic
           
  hours   = divmod(duration_in_s, 3600)  #find number of hours         
  minutes = divmod(hours[1], 60)     #find minutes from remainder           
  seconds = divmod(minutes[1], 1)   #assign remaining seconds

        #publish results
  await ctx.send("it has been:  %d hours, %d minutes and %d seconds" % (hours[0], minutes[0], seconds[0]))


@slash.slash(name="look", description="reads the saved time", guild_ids=guild_ids)
async def _look(ctx: SlashContext):
  
  tz = pytz.timezone('America/Toronto')
  utc_store = datetime.datetime.strptime(db["uses"], "%d-%b-%Y (%H:%M:%S)")
  tz_store = utc_store.astimezone(tz).strftime('%D, %H:%M:%S')
  await ctx.send('stored time is: ' + str(tz_store))


#
  #
  #message listener events

@slash.slash(name="add_order", description="adds a new quick order", options=[
  manage_commands.create_option(
    name = "order", 
    description = "The new order option", #Describe arg
    option_type = 3, #option_type 3 is string
    required = True #Make arg required
  
)], guild_ids=guild_ids)
async def _add_order(ctx: SlashContext, order: str):
  
  new_order = order
  update_order(new_order)
  
  #update_messages(usrmessage)
  await ctx.send("New message added.")

@slash.slash(name="list_order", description="lists current options", guild_ids=guild_ids)
async def _list(ctx: SlashContext):
  
  value = db["orders"]
  
  await ctx.send(f'{list(value)}')

@slash.slash(name="delete_order", description="deletes an order by index number", guild_ids=guild_ids, options=[manage_commands.create_option(
  name = "number",
  description = "input index number to delete (0 is first entry)",
  option_type = int,
  required = True
)])
async def _delete_order(ctx: SlashContext, number: int):
  index = number
  delete_order(index)

  await ctx.send(content = "order deleted")


  ##################################################################
  #message listener


@client.event
async def on_message(message):

    msg = message.content
  
    if message.author == client.user:
      return

    if any(word in msg for word in serve_word):
      
      await message.channel.send('I want you to ' + random.choice(db["orders"]))
  
    if message.content.startswith('$hello'):
      await message.channel.send('Hello! Are you ready to serve?')

     #deletes a quick response
    if msg.startswith("$del"):
      user_message = []
      if "orders" in db.keys():
        index = int(msg.split("$del ",1)[1])
        delete_order(index)
        user_message = db["orders"]
      await message.channel.send(user_message)


      
keep_alive()

client.run(os.getenv('TOKEN'))
