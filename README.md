AutoPromo "promotes" apps based on information the pkginfo file.

Hugely Inspired by these:
joshua-d-miller's [munki-promote](https://github.com/joshua-d-miller/munki-promote)

Greg Neagle's
P-O-C makecatalogs with support for autopromotion
https://gist.github.com/gregneagle/dc05568138638d1f137e

Borrows the git function from Gusto's autopkg_tools
https://github.com/Gusto/it-cpe-opensource/blob/main/autopkg/autopkg_tools.py

## Why?
I wanted to promote apps from testing to production automagically.
I wanted to write something in python.
I wanted different promotion dates if required.

## What does it do?
AutoPromo "moves/promotes" apps between catalogs based on information contained in the pkginfo file stored in a munki repo.
For example it can promote an app from the testing catalog to the production catalog.
When an app is promoted a slack notification is sent.

## Requirements
- A Munki Repo
- Additional information added the pkginfo
- MacAdmins Python 3
- Additional information in pkginfo
- Slack Webhook

## Setup
In the `AutoPromo` script you need to set the following variables:
```python
# Set Variables
munki_repo = "path/to/munki/repo"

# Slack Variables
webhook_url = "https://hooks.slack.com/services/xxxxxxxxxxxxx"
channel = "channel_name"
icon_url = ":arrow_up:"
slack_username = "AutoPromo"

makecatalogs_binary = "/usr/local/munki/makecatalogs"
```


Each app that you want to promote need to have the following added to its pkginfo file:

```xml
<key>_autopromotion_catalogs</key>
<dict>
	<key>7</key>
	<array>
		<string>production</string>
	</array>
</dict>
```

`<key>7</key>` is the number of days until promotion.
`<string>production</string>` is the catalog to promote to.

If you're using autopkg to populate your munki repo, then the autopromotion information can be added to your recipe override. 

## How it works
The script checks each pkginfo file for `_autopromotion_catalogs` if that is found the script will use the `creation_date` sorted in pkginfo and the number of days key to work if the app should be promoted.

I'm using `creation_date` as this is the date autopkg added the app to our repo.

If an app is promoted the following happens:
- A slack notification is sent to our monitoring channel
- `makecatlogs` is run
- The changes are push to git.

Example Slack Notification

![Slack Message](https://github.com/notverypc/AutoPromo/blob/main/SlackNotification.png)

## How we run it
We run the `AutoPromo` script as part of our nightly autopkg run using a GitLab runner:

 ![GitLab Pipeline](https://github.com/notverypc/AutoPromo/blob/main/Pipeline.png)

## Example pkginfo file:

(https://github.com/notverypc/AutoPromo/blob/main/FirefoxLatest.munki.recipe)
