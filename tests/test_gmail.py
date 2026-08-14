from agentdock.gmail import format_messages, parse_message


def test_parse_and_format_message() -> None:
    raw = {
        "id": "abc",
        "snippet": "Please review the attached report.",
        "payload": {"headers": [
            {"name": "From", "value": "Alex <alex@example.com>"},
            {"name": "Subject", "value": "Quarterly report"},
            {"name": "Date", "value": "Fri, 15 Aug 2026 09:00:00 +0000"},
        ]},
    }
    message = parse_message(raw)
    assert message.subject == "Quarterly report"
    assert "alex@example.com" in format_messages([message])


def test_format_empty_messages() -> None:
    assert format_messages([]) == "No messages found."
