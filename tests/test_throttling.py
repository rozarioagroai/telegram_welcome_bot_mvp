import time
from src.services.throttling import Throttler

def test_throttling_basic():
    t = Throttler()
    allowed, retry = t.check(1, "start", 2)
    assert allowed and retry == 0

    allowed2, retry2 = t.check(1, "start", 2)
    assert not allowed2
    assert 0 < retry2 <= 2

    # after sleep it should allow
    time.sleep(2)
    allowed3, retry3 = t.check(1, "start", 2)
    assert allowed3 and retry3 == 0