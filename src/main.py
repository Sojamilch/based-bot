import discord
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as: {client.user}')
