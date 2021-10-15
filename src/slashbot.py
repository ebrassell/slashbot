import inspect
import hmac
import hashlib
import json
import boto3
import requests
import sys
import time
import inspect
from urllib.parse import parse_qs

route_list = []

SLACK_SIGNING_SECRET = ""
SLACK_AUTHENTICATE_REQUEST = True


def get_route(full_command, routes):
    command = full_command.split()[0].lower()[
        1:
    ]  # just the slash command, remove the slash
    # lets only look through routes that are correct command or default
    filtered_routes = [r for r in routes if r["slash"] in [command, "*"]]

    def word_count(route_entry):
        if route_entry["verb"] == "*":  # force wildcards to be considered last
            return 0
        return len(route_entry["verb"].split())

    clean_command = " ".join([word.lower() for word in full_command.split()[1:]])
    # brute force method, look through routes in order of # of words desc.
    sortedroutes = sorted(filtered_routes, key=word_count, reverse=True)
    for r in sortedroutes:
        route_verb = r["verb"]
        # add a space to both sides to black partial matches
        if (clean_command + " ").startswith(route_verb + " ") or route_verb == "*":
            return r
    # if there is no match return none
    return None


class SlashCommand:
    def __init__(self, event) -> None:
        self._payload = event.get("payload")
        self._params = parse_qs(event["body"])
        if not self._params.get("text"):
            self._text = self._params.get("command")[0]
            self.provided_verb = None
        else:
            self._text = (
                self._params.get("command")[0] + " " + self._params.get("text")[0]
            )
            self.provided_verb = self._text.split()[1]
        self.channel_id = self._params.get("channel_id")[0]
        self.channel_name = self._params.get("channel_name")[0]
        self.user_id = self._params.get("user_id")[0]
        self.user_name = self._params.get("user_name")[0]
        self.slash_text = self._params.get("command")[0][
            1:
        ]  # we remove the \ from the left
        self.response_url = self._params.get("response_url")[0]
        self.team_domain = self._params.get("team_domain")[0]
        self.is_callback = event.get("is_callback")
        self.route = get_route(self._text, route_list)
        if self.route:
            print(self.route)
            self.verb = self.route.get("verb")
            verb_word_count = len(self.verb.split())
            if self.verb == "*":
                verb_word_count = 0
            else:
                verb_word_count = len(self.verb.split())
            self.command_args = self._text.split()[verb_word_count + 1 :]
        else:
            self.verb = self._text.split()[1]

    def __str__(self):
        retval = f"""("slash_text":"{self.slash_text}")"""
        return retval


def invoke_lambda(lambda_name: str, payload: dict):
    payload_str = str.encode(json.dumps(payload))
    if "pytest" not in sys.modules:  #
        boto3.client("lambda").invoke(
            FunctionName=lambda_name, Payload=payload_str, InvocationType="Event"
        )


def send_delayed_reply(url, msg, private=False, attachments=None):
    if "pytest" in sys.modules:
        return
    data = {"text": msg, "response_type": "ephemeral" if private else "in_channel"}
    if attachments:
        data["attachments"] = attachments
    RESPONSE = requests.post(
        url, data=json.dumps(data), headers={"Content-Type": "application/json"}
    )
    if RESPONSE.status_code != 200:
        raise ValueError(
            "Request to slack returned an error %s, the response is:\n%s"
            % (RESPONSE.status_code, RESPONSE.text)
        )


def route(verb, acl=None, slash="*"):
    if acl and type(acl) == str:
        user_list = [acl]
    elif type(acl) == list:
        user_list = acl
    else:
        user_list = []
    if slash and type(slash) == str:
        slash_list = [slash]
    elif type(slash) == list:
        slash_list = slash
    else:
        slash_list = ["*"]

    def inner_decorator(f):
        for slash in slash_list:
            entry = {
                "verb": verb.lower(),
                "handler": f,
                "acl": user_list,
                "slash": slash,
            }
        route_list.append(entry)
        return f

    return inner_decorator


def authenticate(event):
    if not SLACK_AUTHENTICATE_REQUEST:
        return True
    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack, so let's ignore it.
    timestamp = event["headers"]["X-Slack-Request-Timestamp"]
    if abs(time.time() - float(timestamp)) > 60 * 5:
        # check for replay attach
        if "pytest" not in sys.modules:
            # suppress this check when under test
            raise (Exception("Invalid request due to timestamp"))
    sig_basestring = "v0:" + timestamp + ":" + event["body"]

    my_signature = (
        "v0="
        + hmac.new(
            bytes(SLACK_SIGNING_SECRET, "utf-8"),
            msg=bytes(sig_basestring, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
    )

    slack_signature = event["headers"]["X-Slack-Signature"]
    if slack_signature != my_signature:
        raise (Exception("Invalid request due to signature"))

    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack, so let's ignore it.
    return True


def handle(cmd: SlashCommand):
    # route_entry = SlashCommand.
    if not cmd.route:
        reply = f"{cmd.verb} is not a valid command."
        return reply
    if cmd.is_callback:
        handler = cmd.route["handler"]
    else:  # is a callback
        return ""
    acl = cmd.route.get("acl")
    if acl and cmd.user_name not in acl:
        reply = f"User {cmd.user_name} not authorized to execute {cmd.verb}"
        return reply
    fn_response = handler(cmd)
    if type(fn_response) == tuple:
        reply = fn_response[0]
        suppress_callback = fn_response[1]
    else:
        reply = fn_response
        suppress_callback = False  # Dont suppress callback is default behavior
    return reply


def build_response(msg: str) -> dict:
    body = {"response_type": "in_channel", "text": msg}
    json_response = {"statusCode": 200, "body": json.dumps(body)}
    return json_response


def main(event, context):
    authenticate(event)
    cmd = SlashCommand(event)
    acl = cmd.route.get("acl")
    if not cmd.route:
        reply = f"{cmd.verb} is not a valid command."
        return build_response(reply)
    if acl and cmd.user_name not in acl:
        reply = f"User {cmd.user_name} not authorized to execute {cmd.verb}"
        return build_response(reply)
    if not event.get("is_callback"):
        event_clone = event.copy()
        event_clone["is_callback"] = True
        invoke_lambda(context.function_name, event_clone)
        return build_response("")
    reply = handle(cmd)
    send_delayed_reply(cmd.response_url, reply)
    return reply
