import discord
from discord.ext import commands
from discord import Embed
from dotenv import load_dotenv
import os
import aiosqlite
import sys

# Wczytanie .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot
bot = commands.Bot(command_prefix='!', intents=intents)

DATABASE = "database.db"


# Tworzenie bazy danych
async def setup_database():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS strefy (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                strefy INTEGER DEFAULT 0
            )
        """)
        await db.commit()


# Funkcja odświeżania topki
async def refresh_topka():

    for guild in bot.guilds:

        channel = discord.utils.get(
            guild.text_channels,
            name="⭐topka-stref"
        )

        if channel is None:
            continue

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                "SELECT username, strefy FROM strefy ORDER BY strefy DESC LIMIT 10"
            )

            rows = await cursor.fetchall()

        ranking = ""

        for index, row in enumerate(rows, start=1):
            ranking += f"{index}. {row[0]} — {row[1]} stref
"

        if ranking == "":
            ranking = "Brak danych."

        embed = Embed(
            title="🏆 TOP 10 STREF",
            description=ranking,
            color=discord.Color.gold()
        )

        messages = [msg async for msg in channel.history(limit=20)]

        bot_message = None

        for msg in messages:
            if msg.author.id == bot.user.id and msg.embeds:
                bot_message = msg
                break

        if bot_message:
            await bot_message.edit(embed=embed)
        else:
            await channel.send(embed=embed)

bot.run(TOKEN)
