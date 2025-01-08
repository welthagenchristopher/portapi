import os
import logging
import requests
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from ._formatter import Format


class ContainerHandler(commands.Cog):
   
    def __init__(self, bot: commands.Bot):
        self.format = Format()
        load_dotenv()
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self.header = {
            "Cache-Control": "no-cache",  # Fixed typo: 'no-chache'
            "Ocp-Apim-Subscription-Key": os.getenv("PORTKEY"),
        }

    def container_request(self, container: str):
        
        url = f"https://api.portconnect.io/v1/container-visits?containerNumber={container}"

        try:
            response = requests.get(url, headers=self.header)
            status_code = response.status_code

            if status_code != 200:
                self.logger.error(f"API call failed with status code: {status_code}")
                return None, status_code

            results = response.json()
            if not results:
                self.logger.info("Container not found in the Port Connect database.")
                return None, status_code

            result = results[0]
            if result["category"] == "EXPORT":
                return self.format.outcontainer(result), status_code
            elif result["category"] == "IMPORT":
                return self.format.incontainer(result), status_code

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during container request: {e}")
            return None, 500

    @discord.app_commands.command()
    async def container(self, interaction: discord.Interaction, container: str):
        
        await interaction.response.defer()

        content, status_code = self.container_request(container)

        if content is None:
            if status_code == 200:
                self.logger.info(
                    "Container not found in the Port Connect database. Check for typos."
                )
                await interaction.followup.send(
                    "Container not found in the Port Connect database. Please check for typos."
                )
            else:
                self.logger.error(f"Failed to retrieve container data (HTTP {status_code}).")
                await interaction.followup.send(
                    "Error retrieving container data. Please try again later."
                )
            return

        self.logger.info("Container-visit call successfully completed. Data returned.")
        embed = discord.Embed(title=content["container"])
        embed.set_author(name="Container Information")

        for key, value in content.items():
            embed.add_field(name=key, value=value, inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    await bot.add_cog(ContainerHandler(bot))
