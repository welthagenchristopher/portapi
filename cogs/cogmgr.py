import os
import time
import logging
import traceback
import discord
from discord.ext import commands


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
    ):  # The app commands that I explained my brief struggle with in #main.py,
        # Notice the 'defer()' method. Using this essentially results in an HTTP,
        # response of 'noted, waiting out for the resulting data', and prevents,
        # the server from slapping you with a timeout error.
      
        await interaction.response.defer()
        self.logger.info(f"Reload command triggered with extension: {extension}")

        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            await interaction.followup.send("Extension directory not found.")
            return

        if extension and extension[0] != "_":
            try:
                await self.bot.unload_extension(f"{self.ext_dir}.{extension}")
                self.logger.info(f"Unloaded extension {extension}")
                await self.bot.load_extension(f"{self.ext_dir}.{extension}")
                self.logger.info(f"Loaded extension {extension}") # The reasion for this very convoluted and manual use of unload, and reload here,
                                                                  # is because at the time, I was experiencing an issue where reloading ,
                                                                  # the modules would work, but the update would not be applied to their functionality.

                                                                  # I finally got it working after realising application commands had to be reloaded,
                                                                  # AND re-synced. Hence the resync() command. The only reason this process worked is
                                                                  # because calling the load() method also syncs the commands - whereas reload() does not.
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
    async def resync(self, interaction: discord.Interaction): # The app commands that I explained my brief struggle with in #main.py,
                                                              # Notice the 'defer()' method. Using this essentially results in an HTTP,
                                                              # response of 'noted, waiting out for the resulting data', and prevents,
                                                              # the server from slapping you with a timeout error.
     
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
