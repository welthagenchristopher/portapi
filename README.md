# portapi
a wrapper for the Port Connect API, built into a discord bot

This project is complete - in a sense. It handles a few different calls to the PortConnect API - and is set up for additional modules to be added
with no change to the main classes. However, this was written a while ago - and while I certainly could do a better job now, were I to re-write this
from the ground up, I still learnt a lot, and encountered a few edge-cases and trip-ups that I thought I'd point out here, for the benefit of others.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

**To get the basic stuff out of the way first - this is a very dependency-light bot. It utilises the Discord.py, and Requests libraries. dotenv can be forgotten post development - its much easier, and safer to use docker secrets, or google run's environment secrets.

Everything is self contained - there is no external config drawn from anywhere, though obviously you cannot use this without authenticating with the 
PortConnect API - which is a paid service. Nonetheless; plug in any exposed api routes and you're good to go.**

--------------------------------------------------------------------------------------------------------------------------------------------------------------

Now, regarding some of the hard-learned lessons I encountered.

   Using the discord API is made extremely easy by use of the libraries developed by people much smarter than I am. However, knowing how to structure the
   interactions between your bot, your server, and the API will go a long way in helping you avoid seemingly out-of-place errors.
   
   Personally, I encountered major issues with the _Application command tree_, namely in performing simple actions like syncing, and registering.
   Some things to note, when using these:

   
   Registration and syncing of these commands has to be deferred, which becomes especially true the more servers your bot is present in.
   Remember that application commands are registered against the bot - not against particular servers, or shards, or instances.
   
   Something to note with using defer(): this invoke requires a followup() response, after the data has been recieved. However, only one
   followup() may be used in response to a defer() call. Syntactically, you cannot have more than one present. What isn't mentioned, is that
   any communication with the API behaves the same as followup() - so while you need one of these, you can then handle any other exception
   respones, or function calls, etc with generic discord.py calls.
   
   Reload functionality for external modules is all well and good when it comes to generic bot commands (commands invoked with the defined
   prefix). However, application commands need to be reloaded, AND re-synced. this can be handled with dedicated reload, and resync commands, or
   alternatively, just calling 'load_extension()' - because this method is designed as an off-brand registration for commands, that also syncs the
   commands present in the extension.
   
   Timemout exceptions are normally quite easily identified with API responses - however, a significant portion of Discord.Py's functionality is
   designed to fail silently in regards to contextually insignificant request errors. Make use of _discord.errors.HTTPException_ to catch these,
   where you can then read the _Retry-After_ value in the header to properly configure your retry functionality.


   Final point in regards to this project - the steps of initialising, registering, and syncing is important, and can have severe impacts against the
   performance and overheard of your bot. Make sure you use methods like setup_hook, on_ready, or on_connect properly.

----------------------------------------------------------------------------------------------------------------------------------------------------------------

Finally, make sure to check out https://discordpy.readthedocs.io/en/stable/index.html - there is a tonne of information, and functionality I didn't even touch on 
with this project. If you want to use the project to get a basic understanding of bot creation, I'd highly recommend educating yourself on sharding, sessions, and
the async functionality. These are all pre-requisites to creating multi-server bots.



