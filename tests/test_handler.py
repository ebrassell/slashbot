import slashbot
from slashbot import SlashCommand

slashbot.SLACK_AUTHENTICATE_REQUEST = False


class context:
    def __init__(self, function_name) -> None:
        self.function_name = function_name


mock_context = context("myfunction")

mock_request = {
    "resource": "/slash",
    "path": "/slash",
    "httpMethod": "POST",
    "headers": {
        "Accept": "application/json,*/*",
        "Accept-Encoding": "gzip,deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Slack-Request-Timestamp": "1633272639",
        "X-Slack-Signature": "v0=8616e7073585809f71c3243d8ec13e3b745f343756f664aab6bfc6be4b1a9af6",
    },
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": None,
    "stageVariables": None,
    "requestContext": {
        "resourceId": "1rgugh",
        "resourcePath": "/slash",
        "httpMethod": "POST",
        "extendedRequestId": "GotyCGYoIAMFeIA=",
        "requestTime": "03/Oct/2021:14:50:40 +0000",
        "path": "/dev/slash",
        "accountId": "252741638415",
        "protocol": "HTTP/1.1",
        "stage": "dev",
        "domainPrefix": "41jdlgwgh7",
        "requestTimeEpoch": 1633272640039,
        "requestId": "6f94435a-154e-492e-a300-b69bda433a63",
        "domainName": "41jdlgwgh7.execute-api.us-east-1.amazonaws.com",
        "apiId": "41jdlgwgh7",
    },
    "body": "team_id=T7197RQTW&team_domain=kinofchris&channel_id=D72A6MK71&channel_name=directmessage&user_id=U717JAPB4&user_name=ericb&command=%2Fslash&text=hello%20arg1%20arg2&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT7197RQTW%2F2584040088448%2FezwsvXewjS35AunSc0EK9lBq",
    "isBase64Encoded": False,
}


@slashbot.route("hello")
def hello(command: slashbot.SlashCommand):
    return f"Hello"

@slashbot.route("twostep")
def step1(command: slashbot.SlashCommand):
    return f"twostep"

@slashbot.route("*", slash='noverb')
def noverb(command: slashbot.SlashCommand):
    return f"noverb"

def test_constructor():
    cmd = SlashCommand(mock_request)
    print(cmd)
    assert cmd.slash_text == "slash"
    assert cmd.verb == "hello"
    assert cmd.command_args[0] == "arg1"
    assert cmd.provided_verb == "hello"


def test_main():
    response = slashbot.main(mock_request, mock_context)
    assert response["statusCode"] == 200

def test_callback():
    request_copy=mock_request.copy()
    mock_request["body"] = "team_id=T&team_domain=k&channel_id=D&channel_name=d&user_id=U&user_name=ericb&command=%2Fslash&text=twostep%20arg1%20arg2&response_url=x"
    request_copy=mock_request.copy()
    cmd = SlashCommand(mock_request)
    assert cmd.verb == "twostep"
    assert not cmd.is_callback
    response = slashbot.main(mock_request, mock_context)
    assert response["statusCode"] == 200
    request_copy['is_callback']=True
    cmd = SlashCommand(request_copy)
    assert cmd.verb == "twostep"
    assert cmd.is_callback
    response = slashbot.main(request_copy, mock_context)
    assert response=='twostep'

def test_noverb():
    request_copy=mock_request.copy()
    request_copy["body"] = "team_id=T&team_domain=k&channel_id=D&channel_name=d&user_id=U&user_name=ericb&command=%2Fnoverb&text=arg1%20arg2%20arg3&response_url=x"
    cmd = SlashCommand(request_copy)
    assert cmd.verb=="*"
    assert cmd.command_args
    assert cmd.command_args[0]=='arg1'
