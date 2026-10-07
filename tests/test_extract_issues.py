from datetime import datetime, timezone

from extract_issues import fetch_issues


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, items, next_url=None, remaining=100):
        self._items = items
        self.links = {"next": {"url": next_url}} if next_url else {}
        self.headers = {"X-RateLimit-Remaining": str(remaining)}

    def raise_for_status(self):
        pass  # A real response raises on HTTP errors; the fake never fails

    def json(self):
        return self._items


class FakeSession:
    """Returns pre-defined responses in order and records every call it receives."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params})
        return next(self._responses)


def test_fetch_issues_follows_pagination():
    # Arrange: two pages of results; page 1 points to page 2 via the 'next' link
    page_1 = FakeResponse(
        [{"id": 1}, {"id": 2}], next_url="https://api.github.com/page2"
    )
    page_2 = FakeResponse([{"id": 3}])
    session = FakeSession([page_1, page_2])
    since = datetime(2026, 9, 1, tzinfo=timezone.utc)

    # Act
    issues = list(fetch_issues(session, "owner/repo", since))

    # Assert: all items from both pages were returned, in order
    assert [i["id"] for i in issues] == [1, 2, 3]
    assert len(session.calls) == 2
    # First call sends the query params; the 'next' URL already embeds them
    assert session.calls[0]["params"]["since"] == "2026-09-01T00:00:00Z"
    assert session.calls[1]["params"] is None
    assert session.calls[1]["url"] == "https://api.github.com/page2"