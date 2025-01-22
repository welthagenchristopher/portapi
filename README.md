# portapi
a wrapper for the Port Connect API, built into a discord bot

Early stages with limited functionality.

Everything you'd need to get a bot up and running, and then begin adding your own commands in is here.

Below are some of the points I'll address when I return to the project:

1. An alternative to the sh*t-show that is _formatter.py would be using BaseModel from pydantic - but with the low
   performance needs, and it being my first time dealing with large JSON responses, I needed the visibility of the json dicts.

2. Error and exception handling -100% can be simplified and handled within its own class, as is the case when 99% of
   the errors are going to involve HTTP requests.

3. the logic in cogmgr.py - don't know why I specifically excluded that file in extension handling, and it pains me that I
   didn't follow the leading with a _ convention, but it'll be fixed.

4. I've got auth headers declared all over the place, this should really have been seperated and handled in its own file / class.

   



