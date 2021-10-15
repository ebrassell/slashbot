# slashbot
Slashbot makes it easy to create Slack slash commands using AWS Lambda functions. These can be handy for creating a secure way to execute automated tasks, even from a mobile device. Perfect for developing "chatops" type applications.

Features:
* Uses Slack Apps API (rather than the legacy slash command API)
* Authenticates requests following Slack recommended best practice (https://api.slack.com/authentication/verifying-requests-from-slack)
* Supports multiple slash commands with a single bot
* Enables limiting certain commands to specific users via a simple ACL model.

## Installation

pip install slashbot [--target=source_directory] 
(the --target option is used to include your packages in your source folder so they willl be included in your AWS Lambda artifact)


## Usage

```python
import os
import slashbot

# https://api.slack.com/authentication/verifying-requests-from-slack
slashbot.SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# Define a default response
@slashbot.route("*")
def default(cmd: slashbot.SlashCommand):
    if not cmd.provided_verb: #Nothing beyond the slash command
        return help(cmd)
    return (
        f"This is a default response. `{cmd.provided_verb}` is not a recognized command. \n"
        + help(cmd)
    )

@slashbot.route("help")
#Handlers take a SlashCommand as input and return text
def help(cmd: slashbot.SlashCommand):
    return f"Here is some helpful text"


@slashbot.route("hello")
def functionnamesdontmatter(cmd: slashbot.SlashCommand):
    return f"Hello {cmd.user_name}"

#This is your AWS Lambda event handler
def handler(event, context):
    return slashbot.main(event, context)

```


## Todo

* Add CI/CD
* Validation on routes to detect conflicting/duplicate entries
* Slack APP Manifest

