from main_app import handle_command, is_wake_word


def test_wake_word():
    assert is_wake_word("hey shark") is True


def test_unknown_wake_word():
    assert is_wake_word("hello computer") is False


def test_name_command():
    response = handle_command("what is your name")
    assert "HeyShark" in response


def test_empty_command():
    response = handle_command("")
    assert isinstance(response, str)