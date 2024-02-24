import asyncio
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import aiohttp
import discord
from discord.ext import commands

from cogs._config import OWNERS, TOKEN, prefix
from core import formatter, help

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"


class Bot(commands.Bot):
    def __init__(self) -> None:
        self.start_time = datetime.now(timezone.utc)
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            help_command=help.HelpMenu(),
            case_insensitive=True,
        )

        self.session: aiohttp.ClientSession
        formatter.install("discord", "INFO")
        formatter.install("bot", "INFO")
        self.logger = logging.getLogger("bot")

    async def setup_hook(self):
        await self.load_extension("jishaku")
        await self.load_cogs()

    async def load_cogs(self):
        s = time.perf_counter()
        for file in os.listdir("cogs/"):
            if file.endswith(".py") and not file.startswith("_"):
                extension = f"cogs.{file[:-3]}"
                try:
                    await self.load_extension(extension)
                    self.logger.info(f"Loaded - {extension}")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.exception(f"Failed to load extension {extension}. - {exception}")
                    traceback.print_exc()

        elapsed = time.perf_counter() - s
        self.logger.info(f"Loaded all extensions - took {elapsed:.2f}s")

    async def is_owner(self, user: discord.abc.User):
        if user.id in OWNERS:
            return True
        # Else fall back to the original
        return await super().is_owner(user)

    async def on_ready(self) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)
        await self.tree.sync()
        await self.change_presence(activity=discord.Game(name="Free Media Heck Yeah"))
        self.logger.info("Bot is ready!")


async def main() -> None:
    async with aiohttp.ClientSession() as session, Bot() as boat:
        await boat.start(TOKEN, reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
