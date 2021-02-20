import discord
import os
import time

client = discord.Client()

TOKEN="ODEwMjM3NDc0MjM2MTM3NTAy.YCgucw.HVFQbzrWTBe4ZKDwnSgFa_-Y5Xs"
# 'global' variables
INVOCATION_PREFIX = "!"
CREATE_COMMAND = "create"
JOIN_COMMAND = "join"
HELP_COMMAND = "help"
LEAVE_COMMAND = "leave"
DELETE_COMMAND = "del"
FORBIDDEN_NAMES = ["Organizer","Judge","Hacker","Mentor","Presenter","Bot","rules","start-here","announcements","music","gaming","movies","Gaming","Music","Movie Theater","general","looking-for-team","General","General 2","ask-mentor","ask-organizer","ask-mlh","Help","Help 2","Mentor Help","Mentor Waiting Room","organizer-text","Organizer Voice","judge-text","Waiting Room","Judge 1","bot-commands","music-bots"]
@client.event
async def on_member_join(member):
  await member.guild.system_channel.send("Welcome, " + member.name)
  await member.send("Welcome")
  print("Done")

@client.event
async def on_ready():
  '''Called when client is ready. Prints the bot's current user.'''
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Game(name=" use !help to see the commands!"))

@client.event
async def on_raw_reaction_add(payload):
  print("test")
  if payload.channel_id == 805214121163358288:
    print(str(payload.emoji))
    if str(payload.emoji) == "✅":
      await payload.member.add_roles(discord.utils.get(payload.member.guild.roles,name=("Hacker")))
      print("testtt")

@client.event
async def on_message(message):
  """Called whenever a message is sent. Handles commands.

  Parameters: a Message object"""
  if message.author == client.user:
    #if the message recieved is from the bot, discard
    return

  if len(message.content) == 0:
    #if the message recieved is null, discard
    return

  if message.content[0] != INVOCATION_PREFIX:
    #if the message recieved not a command for the bot, discard
    return


  command = parseCommand(message)
  call = command[0] #call is the first command i.e join, create, leave, help
  print(call)
  if call == HELP_COMMAND: #help command
    await dissapMessage(message,doHelp())

  if call == CREATE_COMMAND: #create team command
    await createTeam(message,command)

  if call == JOIN_COMMAND: #join team command
    await joinTeam(message,command)

  if call == LEAVE_COMMAND: #leave team command
    await leaveTeam(message,command)

  if call == DELETE_COMMAND: #delete team command
    await deleteTeam(message,command)

  await message.delete()




def parseCommand(message):
  """Parses the command into a list of Strings.

  Returns: A list of Strings"""
  #splits the message into a list of strings and discards the INVOCATION_PREFIX
  command = message.content[1:].split(" ")
  command[0].lower
  return command

def doHelp():
  """Constructs the help String.

  Returns: A String"""

  #constructs the string starting with a quote prifx
  outString = ">>> "
  #create command
  outString += "**" + INVOCATION_PREFIX + CREATE_COMMAND + "**" + " *[team_name]* will create a team, with name team_name, and assign the user to that team \n"
  #join command
  outString += "**" + INVOCATION_PREFIX + JOIN_COMMAND + "**" + " *[team_name]* will assign the user to the team \n"
  #leave command
  outString += "**" + INVOCATION_PREFIX + LEAVE_COMMAND + "**" + " *[team_name]* will deassign the user from the team \n"
  #del command
  outString += "**" + INVOCATION_PREFIX + DELETE_COMMAND + "**" + " *[team_name]* will **PERMANENTLY** delete the team and all channels associated. \n"
  #returns the created string
  return outString

async def createTeam(message,command):
  """Creates a text and voice channel for a given team. Creates a role for a given team and auto-assigns the author to it.

  Returns: Role object of role that has been created"""
  teamName = collapseParams(command)
  if not findTeam(message,teamName):
    #team does not exist

    category = discord.utils.get(message.guild.categories, name = "Teams")

    #creates a role for the team
    teamRole = await message.guild.create_role(name=teamName,colour=discord.Colour.random(),hoist=True,mentionable=True)

    #creates the text and voice channels for the team
    teamText = await message.guild.create_text_channel(teamName)
    teamVoice = await message.guild.create_voice_channel(teamName)

    #set permissions for the newly created text and voice channels
    await teamText.set_permissions(message.guild.default_role,read_messages=False)
    await teamVoice.set_permissions(message.guild.default_role,view_channel=False)
    await teamText.set_permissions(findSensitiveTeam(message,"Judge"),read_messages=True)
    await teamVoice.set_permissions(findSensitiveTeam(message,"Judge"),view_channel=True)
    await teamText.set_permissions(teamRole,read_messages=True)
    await teamVoice.set_permissions(teamRole,view_channel=True)

    #adds the newly created role to the author of the message
    await message.author.add_roles(teamRole)

    #sends message notifying user
    await dissapMessage(message,"Team created!")
    return teamRole
  else:
    #team already exists
    await dissapMessage(message,"That team already exists, try joining with the join commmand, or try another team name.")

    return None

async def joinTeam(message,command):
  """Gives the author the role for the team specified, if it exists."""
  #finds the specified team, returns a bool
  team = findTeam(message,collapseParams(command))

  if team:
    #team exists

    #adds role to author
    await message.author.add_roles(team)

    #sends user a message to notify
    await message.channel.send("If you were not already in that team, the role has been added.")
  else:
    #team doe not exist
    await message.channel.send("That role does not exist.")

def findTeam(message,teamName):
  """Checks if Role with specified name exists. Will only return the first role with given name.

  Returns: first Role object with specified name"""
  if teamName in FORBIDDEN_NAMES:
    return None
  return discord.utils.get(message.guild.roles,name=(teamName))

def findSensitiveTeam(message,teamName):
  return discord.utils.get(message.guild.roles,name=(teamName))

def findChannel(message,channelName):
  """Checks if Channel with specified name exists. Will only return the first channel with given name.

  Returns: first Channel object with specified name"""
  return discord.utils.get(message.guild.channels,name=(channelName))

async def leaveTeam(message,command):
  """Removes from the author the role for the team specified, if it exists."""

  #checks if team exists
  team = findTeam(message,collapseParams(command))

  if team:
    #team exists

    #removes the role from the user
    await message.author.remove_roles(team)

    #sends a message to notify the user
    await dissapMessage(message,"Role removed.")
  else:
    #team does not exist

    await dissapMessage(message,"That role does not exist.")

def collapseParams(command):
  """Collapses the parameters (parsed command list) into a single string
  Parameters: List of Strings
  Returns: String"""

  #initialises blank string
  outString = ""
  #for every parameter except the first parameter
  for i in command[1:]:
    #add to outString
    outString+=i + " "
  #returns newly created String
  return outString[:-1]

async def deleteTeam(message,command):
  """Deletes a given role from the author and deletes the corresponding text channel and voice channel for that role.
  Parameters: Mesage object, list of Strings"""


  teamName = collapseParams(command)
  if findTeam(message,teamName) in message.author.roles:
    team = findTeam(message,teamName)
    print(team)
    await team.delete()
    await findChannel(message,teamName).delete()
    await (findChannel(message,teamName.lower().replace(" ","-"))).delete()
    await dissapMessage(message,"Team has been deleted! :( ")

async def dissapMessage(message,output):
  sent = await message.channel.send(output)
  time.sleep(10)
  await sent.delete()
#runs the client
client.run(TOKEN)