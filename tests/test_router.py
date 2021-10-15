from slashbot import get_route


def test_default_route():
    routes = [
        {"verb": "*", "slash": "*", "id": 1}
    ]  # we include an id just to verify we getting the correct entry
    assert get_route("anycommand", routes)["id"] == 1
    assert get_route("anycommand witharg", routes)["id"] == 1


def test_default_route_with_2_differentcomands():
    routes = [
        {"verb": "*", "slash": "cmd1", "id": 1},
        {"verb": "*", "slash": "cmd2", "id": 2},
        {"verb": "*", "slash": "*", "id": 3},
    ]
    assert get_route("/cmd1", routes)["id"] == 1
    assert get_route("/cmd1 withargs", routes)["id"] == 1
    assert get_route("/cmd2", routes)["id"] == 2
    assert get_route("/cmd2 withargs", routes)["id"] == 2
    assert get_route("/anycmd", routes)["id"] == 3
    assert get_route("/anycmd withargs", routes)["id"] == 3


def test_simple():
    routes = [
        {
            "verb": "onewordverb",
            "handler": "dummyval",
            "acl": [],
            "slash": "*",
            "callback": None,
        }
    ]
    assert get_route("anycommand onewordverb", routes)["verb"] == "onewordverb"
    assert get_route("anycommand onewordverb witharg", routes)["verb"] == "onewordverb"
    assert get_route("anycommand", routes) is None
    assert get_route("anycommand onewordverbx", routes) is None


def test_with_multiplewords():
    routes = [
        {"verb": "*", "slash": "*", "id": 1},
        {"verb": "onewordverb", "slash": "*", "id": 2},
        {"verb": "onewordverb twowordverb", "slash": "*", "id": 3},
        {"verb": "onewordverb twowordverb threewordverb", "slash": "*", "id": 4},
    ]
    assert (
        get_route("anycommand oneword", routes)["id"] == 1
    )  # make sure partial words don't match
    assert get_route("anycommand onewordverb", routes)["id"] == 2
    assert get_route("anycommand onewordverb withargs", routes)["id"] == 2
    assert get_route("anycommand onewordverb  twowordverb", routes)["id"] == 3
    assert get_route("anycommand onewordverb twowordverb withargs", routes)["id"] == 3
    assert get_route("anycommand ONEwordverb", routes)["id"] == 2
    assert get_route("anycommand ONEwordverb withargs", routes)["id"] == 2
    assert get_route("anycommand  onewordverb  twowordverb", routes)["id"] == 3
    assert get_route("anycommand ONEwordverb  twowordverb withargs", routes)["id"] == 3


def test_non_default_route_with_2_differentcomands():
    routes = [
        {"verb": "onewordverb", "slash": "cmd1", "id": 1},
        {"verb": "onewordverb", "slash": "cmd2", "id": 2},
        {"verb": "differentverb", "slash": "cmd1", "id": 3},
        {"verb": "*", "slash": "*", "id": 4},
    ]
    assert get_route("/cmd1", routes)["id"] == 4
    assert get_route("/cmd1 onewordverb", routes)["id"] == 1
    assert get_route("/cmd2 onewordverb", routes)["id"] == 2
    assert get_route("/cmd1 differentverb", routes)["id"] == 3
    assert get_route("/cmd2 differentverb", routes)["id"] == 4
    assert get_route("/cmd1 anyverb", routes)["id"] == 4


def test_default_route_with_2_differentcomands():
    routes = [
        {"verb": "*", "slash": "cmd1", "id": 1},
        {"verb": "*", "slash": "cmd2", "id": 2},
        {"verb": "*", "slash": "*", "id": 3},
    ]
    assert get_route("/cmd1", routes)["id"] == 1
    assert get_route("/cmd1 withargs", routes)["id"] == 1
    assert get_route("/cmd2", routes)["id"] == 2
    assert get_route("/cmd2 withargs", routes)["id"] == 2
    assert get_route("/anycmd", routes)["id"] == 3
    assert get_route("/anycmd withargs", routes)["id"] == 3
