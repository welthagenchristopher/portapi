import os
import time
import logging
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv


class CogManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        
        self.bot = bot
        self.ext_dir = "cogs"
        self.logger = logging.getLogger(self.__class__.__name__)

    @discord.app_commands.command()
    async def reload(
        self,
        interaction: discord.Interaction,
        extension: str = None,
    ):
      
        await interaction.response.defer()
        self.logger.info(f"Reload command triggered with extension: {extension}")

        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            await interaction.followup.send("Extension directory not found.")
            return

        if extension and extension != "cogmgr":
            try:
                await self.bot.unload_extension(f"{self.ext_dir}.{extension}")
                self.logger.info(f"Unloaded extension {extension}")
                await self.bot.load_extension(f"{self.ext_dir}.{extension}")
                self.logger.info(f"Loaded extension {extension}")
            except commands.ExtensionError:
                self.logger.error(
                    f"Failed to reload extension {extension}\n"
                    f"{traceback.format_exc()}"
                )
                await interaction.followup.send(
                    f"Failed to reload extension {extension}."
                )
        else:
            for filename in os.listdir(self.ext_dir):
                if (
                    filename.endswith(".py")
                    and not filename.startswith("_")
                    and filename != "cogmgr.py"
                ):
                    try:
                        await self.bot.unload_extension(
                            f"{self.ext_dir}.{filename[:-3]}"
                        )
                        self.logger.info(f"Unloaded extension {filename[:-3]}")
                        await self.bot.load_extension(
                            f"{self.ext_dir}.{filename[:-3]}"
                        )
                        self.logger.info(f"Loaded extension {filename[:-3]}")
                    except commands.ExtensionError:
                        self.logger.error(
                            f"Failed to reload extension {filename[:-3]}\n"
                            f"{traceback.format_exc()}"
                        )
                        await interaction.followup.send(
                            f"Failed to reload extension {filename[:-3]}."
                        )

        reload_message = (
            f"Reloaded {extension}"
            if extension
            else "Reloaded all extensions."
        )
        await interaction.followup.send(reload_message)

    @discord.app_commands.command()
    async def resync(self, interaction: discord.Interaction):
     
        await interaction.response.defer()
        self.logger.info("Syncing commands with Discord...")

        try:
            await self.bot.tree.sync()
            self.logger.info("Successfully synced commands.")
            await interaction.followup.send("Successfully synced commands.")
        except discord.errors.HTTPException as e:
            self.logger.error(f"Error during command sync: {e}")
            await interaction.followup.send("Error syncing commands, see logs.")

            if e.status == 429:
                retry_after = int(e.response.headers.get("Retry-After", 1))
                self.logger.info(f"Retrying in {retry_after} seconds")
                time.sleep(retry_after)


async def setup(bot: commands.Bot):
  
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    await bot.add_cog(CogManager(bot))
