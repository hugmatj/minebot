#
#  The python Minecraft Bot to rule them all.
#  Poggers!
#
#  (c) 2021 by Guido Appenzeller & Daniel Appenzeller
#

from javascript import require, On, Once, AsyncTask, once, off
import time

from account import account
from equipment import *
from mine import *
from chat import *
from farming import *

# Setup and log into server

mineflayer = require('mineflayer')

bot = mineflayer.createBot(
	{   'host'	  : '34.83.26.64', 
		'username': account.account_user, 
		'password': account.account_password, 
		'hideErrors': False, 
    'version': '1.16.5'
	}
)

bot.mcData   = require('minecraft-data')(bot.version)
bot.Block    = require('prismarine-block')(bot.version)
bot.Vec3     = require('vec3').Vec3
bot.callsign = account.account_user[0]

# Setup for the pathfinder plugin

pathfinder = require('mineflayer-pathfinder')
bot.loadPlugin(pathfinder.pathfinder)
# Create a new movements class
movements = pathfinder.Movements(bot, bot.mcData)
movements.blocksToAvoid.delete(bot.mcData.blocksByName.wheat.id)
bot.pathfinder.setMovements(movements)
# How far to be fromt the goal
RANGE_GOAL = 1

time.sleep(2)

#
# Main Loop - We are driven by chat commands
#

bot.stopActivity = True

@On(bot, 'chat')
def onChat(sender, message, this, *rest):
  # check if order is incorrect to fix a bug we are seeing between Guido and Daniel
  if type(sender) != type(""):
    # reorder
    t = sender
    sender = message
    message =  this
    this = t

  if message[0] == bot.callsign and message[1] == '.':
    print(f'{sender} messaged me "{message}"')
    message = message[2:]
  elif sender == account.account_master:
    pass
  else:
    return

  # "stop" should stop all activities

  if 'stop' in message:
    bot.stopActivity = True
  else:
    bot.stopActivity = False

  # come - try to get to the player
  if 'come' in message or 'go' in message:
    if message == 'come':
      player = bot.players[sender]
    elif 'go to' in message:
      player = bot.players[message[6:]]
    else:
      bot.chat("No Clear Target")
    target = player.entity
    if not target:
      bot.chat("I don't see you!")
      return
    pos = target.position
    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

  if 'follow' in message:
    if message == 'follow':
      player = bot.players[sender]
    elif len(message) > 6:
      player = bot.players[message[7:]]
    else:
      bot.chat("No Clear Target")
    target = player.entity
    if not target:
      bot.chat("I don't see you!")
      return
    @AsyncTask(start=True)
    def follow(task):
      while bot.stopActivity != True:
        bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(player.entity, RANGE_GOAL))
        time.sleep(2)

  if message == 'mine':
    @AsyncTask(start=True)
    def doStripMine(task):
      stripMine(bot)

  if message == 'farm':
    @AsyncTask(start=True)
    def doFarmingTask(task):
      doFarming(bot)
 
  if message == 'deposit':
    depositToChest(bot)

  if message == 'status':
    sayStatus(bot)
  if message == 'hello':
    sayHello(bot)
  if message =='inventory':
    printInventory(bot)
  if message == 'eat':
    eatFood(bot)
  if message == 'yeet':
    # exit the game
    off(bot, 'chat', onChat)

def commandSend():
  command = ''
  command = input() 
  return command

@AsyncTask(start=True)
def commandTask(task):
  while True:
    onChat('Command Line', commandSend(), 'this is a placeholder for the real thing')

# Report status
print('Connected, call sign: "'+bot.callsign+'"')
time.sleep(1)
sayStatus(bot)
printInventory(bot)

# The spawn event 
once(bot, 'login')
bot.chat('Bot '+bot.callsign+' joined.')

