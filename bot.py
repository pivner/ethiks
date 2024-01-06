import discord
import os
import sqlite3

from apikeys import *

class MyClient(discord.Client):

    def __init__(self, intents):
        super().__init__(intents=intents)

        # Initialize SQLite3
        self.connection: object = sqlite3.connect('database.db')
        self.cursor: object = self.connection.cursor()

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
                       msg5 TEXT NOT NULL)""")
        
        # Bot is ready
        print(f"Logged on as {self.user}!")

    async def on_message(self, message) -> None:
        if message.author.bot:
            return

        print(f"Message from {message.author}: {message.content}")

if __name__ == '__main__':
    intents: object = discord.Intents.default()
    intents.message_content = True

    client: object = MyClient(intents=intents)
    client.run(BOT_TOKEN)