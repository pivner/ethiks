import discord
import os
import sqlite3

import hateclassify as hc

from apikeys import *
from hateclassify import *

from datetime import timedelta

class MyClient(discord.Client):

    def __init__(self, intents):
        super().__init__(intents=intents)

        # Initialize SQLite3
        self.connection: object = sqlite3.connect('database.sqlite')
        self.cursor: object = self.connection.cursor()
        # self.safety = hc.is_safe(hc.classify())

    async def on_ready(self) -> None:
        # Create database.db if it doesn't exist
        if not os.path.isfile('./database.sqlite'):
            f: object = open('database.sqlite', 'wb')
            print("Created database.sqlite file")
            f.close()

        # Create censorship table if it doesn't exist
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS censorship(
                        user_id INT PRIMARY KEY, 
                        social_credit INT NOT NULL);""")
        
        # Bot is ready
        print(f"Logged on as {self.user}!")

    async def on_message(self, message) -> None:
        if message.author.bot:
            return

        self.cursor.execute(f'INSERT OR IGNORE INTO censorship (user_id, social_credit) VALUES({message.author.id}, 1000);')
       
       
        isSafe, reason, score = is_safe(classify(message.content))

        if not isSafe:
            await message.delete()
            embed: object = discord.Embed(
                title = "Warning!",
                description = f"Please review the following comments carefully before viewing the message sent by <@{message.author.id}> as it may contain sensitive content or misinformation.",
                color = 0xea3e3e
            )
            embed.add_field(name = "", value = f"||{message.content}||", inline = False)
            embed.add_field(name = "", value = reason, inline = False)
            await message.channel.send(embed = embed)
          
            response = self.cursor.execute(f'SELECT social_credit FROM censorship WHERE user_id = {message.author.id}').fetchall()

            # Manages rep score
            newScore = int(response[0][0]) - score*10

            # controls the Direct Message Embed skip over this bit
            directMsg: object = discord.Embed(
                title = "Warning!",
                description = f"Please review the following comments carefully as your message has been flagged for containing sensitive content or misinformation. If you think this is a mistake, please contact server admin. NOOT NOOT!",
                color = 0xfee12b
            )
            directMsg.add_field(name = "You said:", value = f"\"{message.content}\"", inline = False)
            directMsg.add_field(name = "", value = f"You have lost **{score}** Rep.", inline = False)
            directMsg.add_field(name = "", value = f"Your new Rep. Score is **{newScore}**!", inline = False)
            await message.author.send(embed = directMsg)

            if newScore <= 0:
                # Time out logic
                timeout = 10 #seconds
                await message.author.timeout(timedelta(seconds = timeout))
                newScore = 1000
            
                directMsg: object = discord.Embed(
                    title = "Timeout Notice",
                    description = f"Please review the following comments carefully as your message has been flagged for containing sensitive content or misinformation. If you think this is a mistake, please contact server admin. NOOT NOOT!",
                    color = 0xfee12b
                )
                directMsg.add_field(name = "You said:", value = f"\"{message.content}\" \nDue to previous messages including this one, you have received a {timeout} second timeout.", inline = False)
                await message.author.send(embed = directMsg)

            self.cursor.execute(f'REPLACE INTO censorship (user_id, social_credit) VALUES({message.author.id}, {newScore});')
        response = self.cursor.execute(f'SELECT * FROM censorship WHERE user_id = {message.author.id};').fetchall()
        print(response)

        



if __name__ == '__main__':
    intents: object = discord.Intents.default()
    intents.message_content = True

    client: object = MyClient(intents=intents)
    client.run(BOT_TOKEN)