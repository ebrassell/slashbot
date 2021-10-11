# slashbot
Slashbot makes it easy to create slash commands using AWS Lambda functions. These can be handy for creating a secure way to execute automated tasks, even from a mobile device. Perfect for "chatops".

Features:
* Uses Slack's Apps API (rather than the legacy slash command API)
* Authenticates requests following Slack's recommended best practice (https://api.slack.com/authentication/verifying-requests-from-slack)
* Supports multiple slash commands with a single bot
* Enables limiting certain commands to specific users via a simple ACL model.

## Installation

pip install slashbot [--target=source_directory] 
(the --target option is used to include your packages in your source folder so they willl be included in your AWS Lambda artifact)
