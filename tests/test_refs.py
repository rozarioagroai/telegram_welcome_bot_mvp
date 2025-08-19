from src.services.refs import build_url

def test_build_url():
    url = build_url("TEST", "https://example.com/ref", "first_trade")
    assert "https://example.com/ref" in url
    assert "utm_source=telegram" in url
    assert "utm_medium=bot" in url
    assert "utm_campaign=first_trade" in url
    assert "utm_content=TEST" in url