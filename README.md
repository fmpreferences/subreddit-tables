# subreddit-tables
subreddit tables

## Getting started
first go to reddit, apps, then create a script type app, then create praw.ini and put this in it:
```ini
[script:(scriptname):v(version) (by (authorname))]
client_id=your client id
client_secret=your client secret
username=your bots username
password=your bots password
```

then change the user agent (the script:(scriptname):v(version) (by (authorname)) thing) in reddits.py to the proper one.

You need PyGObject to run the GUI. I may port it to an executable later for ease for windows users.