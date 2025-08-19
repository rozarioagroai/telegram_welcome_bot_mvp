from src.utils.tg import parse_start_payload

def test_parse_payload_none():
    assert parse_start_payload("") == "direct"
    assert parse_start_payload("/start") == "direct"

def test_parse_payload_with_arg():
    assert parse_start_payload("/start TEST") == "TEST"
    assert parse_start_payload("/start   abc_123   ") == "abc_123"

def test_parse_payload_fallback_text():
    assert parse_start_payload("ONLYPAYLOAD") == "ONLYPAYLOAD"