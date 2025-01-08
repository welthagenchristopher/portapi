import os
import time
import logging
import traceback
import datetime
import typing
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv


class Portbot(commands.Bot):
    client: aiohttp.ClientSession  # HTTP requests session (not used yet)
    _uptime: datetime.datetime = datetime.datetime.now()
    ext_dir: str  # Directory for extensions (cogs)
    synced: bool = False  # Command sync flag

    def __init__(
        self,
        prefix: str,  # Command prefix
        ext_dir: str,  # Extension directory path
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        
        intents = discord.Intents.default()
        intents.members = True  # Track member updates (e.g., joins, leaves)
        intents.message_content = True  # Allow bot to read message content

        super().__init__(
            *args,
            **kwargs,
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            tree_cls=discord.app_commands.tree.CommandTree,
        )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir

    async def setup_hook(self) -> None:
        
        self.client = aiohttp.ClientSession()
        await self._load_extensions()

    async def on_ready(self) -> None:
        
        self.logger.info(f"Logged in as {self.user}")

        if not self.synced:
            try:
                self.logger.info("Syncing commands with Discord...")
                await self.tree.sync()
                self.logger.info("Successfully synced commands.")
                self.synced = True

                for command in self.tree._global_commands:
                    if isinstance(command, discord.app_commands.Command):
                        self.logger.info(f"Synced command: {command.name}")
                    else:
                        self.logger.error("Unexpected command type")
            except discord.errors.HTTPException as e:
                self.logger.error(f"Error during command sync: {e}")
                if e.status == 429:
                    retry_after = int(
                        e.response.headers.get("Retry-After", 1)
                    )
                    self.logger.info(f"Retrying in {retry_after} seconds")
                    time.sleep(retry_after)

    async def _load_extensions(self) -> None:
        
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            return

        for filename in os.listdir(self.ext_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    self.logger.error(
                        f"Failed to load extension {filename[:-3]}"
                        f"\n{traceback.format_exc()}"
                    )

    async def close(self) -> None:
        
        await super().close()
        await self.client.close()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        
        load_dotenv()
        token = os.getenv("DISCORDKEY")
        if not token:
            self.logger.error("No bot token found! Exiting.")
            exit()

        try:
            self.logger.info("Logging in using static token.")
            super().run(token, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error during bot execution: {e}")
            self.logger.info("Exiting...")
            exit()


def main() -> None:
   
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    bot = Portbot(prefix="!", ext_dir="cogs")
    bot.run()


if __name__ == "__main__":
    main()
