import discord
from apikeys import *

class MyClient(discord.Client):

    async def on_ready(self) -> None:
        print(f'Logged on as {self.user}!')

    async def on_message(self, message) -> None:
        print(f'Message from {message.author}: {message.content}')
        pass

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(BOT_TOKEN)