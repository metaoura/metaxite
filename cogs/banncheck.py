import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import time
import config

class RedirectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        link_button = discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="Join Support Server",
            url="https://discord.gg/JrJYvZDRdc"
        )
        self.add_item(link_button)

class BanCheckCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not getattr(self.bot, "_synced", False):
            await self.bot.tree.sync()
            self.bot._synced = True

    async def fetch_ban_check_data(self, uid: str):
        url = f"{config.API_URL}/{uid}"
        headers = {"Authorization": f"Bearer {config.API_KEY}"}
        start_time = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params={"api_key": config.API_KEY}) as response:
                status_code = response.status
                data = await response.json()
        end_time = time.perf_counter()
        elapsed_s = end_time - start_time
        return status_code, data, elapsed_s

    def create_error_embed(self, status_code: int):
        if status_code == 401:
            return discord.Embed(
                title=":x: Error 401",
                description="API key missing or not provided correctly.",
                color=discord.Color.red()
            )
        elif status_code == 403:
            return discord.Embed(
                title=":x: Error 403",
                description="Invalid or expired API key.",
                color=discord.Color.red()
            )
        elif status_code == 429:
            return discord.Embed(
                title=":x: Error 429",
                description="Daily usage limit reached.",
                color=discord.Color.red()
            )
        elif status_code == 500:
            return discord.Embed(
                title=":x: Error 500",
                description="Server error at BanCheck service.",
                color=discord.Color.red()
            )
        else:
            return discord.Embed(
                title=f":x: Error {status_code}",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )

    def create_embed_from_response(self, status_code: int, data: dict, uid: str, user: discord.abc.User, elapsed_s: float):
        if status_code == 200:
            embed = discord.Embed(
                title=":white_check_mark: Ban Check Result",
                description=f"UID: **{uid}**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🛑 Banned? or ✅",
                value=f"`{data.get('data', {}).get('is_banned', 'Unknown')}`",
                inline=False
            )
            embed.add_field(
                name="⏰ Ban Period",
                value=f"`{data.get('data', {}).get('period_month', 'N/A')}`",
                inline=False
            )
            embed.add_field(
                name="📢 Message",
                value=f"`{data.get('msg', 'N/A')}`",
                inline=False
            )
            embed.add_field(
                name="📊 Usage Count Today",
                value=f"`{data.get('usage_count today', 'N/A')}`",
                inline=False
            )
            embed.add_field(
                name="📆 Daily Limit",
                value=f"`{data.get('daily_limit', 'N/A')}`",
                inline=False
            )
        else:
            embed = self.create_error_embed(status_code)

        embed.set_author(name=user.display_name, icon_url=user.display_avatar)
        embed.set_footer(text=f"Requested by {user.display_name} | {elapsed_s:.2f}s | {config.FOOTER_TEXT}")
        return embed

    @app_commands.command(name="bancheck", description="Check ban status for a given UID.")
    async def slash_bancheck(self, interaction: discord.Interaction, uid: str):
        await interaction.response.defer(thinking=True)
        status_code, data, elapsed_s = await self.fetch_ban_check_data(uid)
        embed = self.create_embed_from_response(status_code, data, uid, interaction.user, elapsed_s)
        await interaction.followup.send(
            content=f"<@{interaction.user.id}>",
            embed=embed,
            view=RedirectView()
        )

    @commands.command(name="bancheck", help="Check ban status for a given UID")
    async def prefix_bancheck(self, ctx: commands.Context, uid: str):
        async with ctx.typing():
            status_code, data, elapsed_s = await self.fetch_ban_check_data(uid)
        embed = self.create_embed_from_response(status_code, data, uid, ctx.author, elapsed_s)
        await ctx.send(
            content=f"<@{ctx.author.id}>",
            embed=embed,
            view=RedirectView()
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(BanCheckCog(bot))
