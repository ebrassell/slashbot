# slashbot
Slashbot makes it easy to create slash commands using AWS Lambda functions. These can be handy for creating a secure way to execute automated tasks, even from a mobile device.

Features:
* Uses Slack Apps API (rather than the legacy slash command API)
* Request authentication following Slack's recommended best practice (https://api.slack.com/authentication/verifying-requests-from-slack)
* Ability to support multiple slash commands with a single bot
* Simple ACL model enables you to limit certain commands to specific users.
