import discord
import os
import sqlite3

from apikeys import *
from hateclassify import *

class MyClient(discord.Client):

    def __init__(self, intents):
        super().__init__(intents=intents)

        # Initialize SQLite3
        self.connection: object = sqlite3.connect('database.db')
        self.cursor: object = self.connection.cursor()
        # self.safety = safety

    async def on_ready(self) -> None:
        # Create database.db if it doesn't exist
        if not os.path.isfile('./database.db'):
            f: object = open('database.db', 'wb')
            print("Created database.db file")
            f.close()

        # Create censorship table if it doesn't exist
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS censorship(
                        user_id INT PRIMARY KEY, 
                        social_credit INT NOT NULL,
                        msg1 TEXT NOT NULL, 
                        msg2 TEXT NOT NULL, 
                        msg3 TEXT NOT NULL, 
                        msg4 TEXT NOT NULL,
                        msg5 TEXT NOT NULL);""")
        
        # Bot is ready
        print(f"Logged on as {self.user}!")

    async def on_message(self, message) -> None:
        if message.author.bot:
            return

        self.cursor.execute(f'INSERT OR IGNORE INTO censorship (user_id, social_credit, msg1, msg2, msg3, msg4, msg5) VALUES({message.author.id}, 1000, "", "", "", "", "");')
        isSafe, reason, score = is_safe(message.content)
        if not isSafe:
            await message.delete()
            embed: object = discord.Embed(
                title = "Warning!",
                description = "Please view the following information carefully and review any comments before viewing the message.",
                color = 0xea3e3e
            )
            name: str = f"The following message from <@{message.author.id}> has been censored"
            embed.add_field(name = name, value = f"||{message.content}||", inline = False)
            embed.add_field(name = "", value = reason, inline = False)
            await message.channel.send(embed = embed)

        response = self.cursor.execute(f'SELECT * FROM censorship WHERE user_id = {message.author.id};').fetchall()
        print(response)


if __name__ == '__main__':
    intents: object = discord.Intents.default()
    intents.message_content = True

    client: object = MyClient(intents=intents)
    client.run(BOT_TOKEN)