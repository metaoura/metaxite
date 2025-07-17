import discord
from discord.ext import commands
import config
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print("[Main] Bot is ready. Attempting slash command sync...")
    try:
        synced_commands = await bot.tree.sync()
        print(f"[Main] Synced {len(synced_commands)} command(s).")
    except Exception as e:
        print(f"[Main] Slash command sync failed: {e}")
    print(f"[Main] Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_connect():
    print("[Main] Bot connected to Discord Gateway.")

async def load_cogs():
    print("[Main] Loading cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"[Main] Loaded extension: {extension}")
            except Exception as e:
                print(f"[Main] Failed to load extension {extension}: {e}")

async def main():
    print("[Main] Inside main function.")
    await load_cogs()
    print("[Main] Starting the bot...")
    await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
