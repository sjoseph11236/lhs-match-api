import pytest
from unittest.mock import patch, MagicMock
from src.lib.adzuna import AdzunaClient


MOCK_RESPONSE = {
    "results": [
        {
            "id":          "abc123",
            "title":       "Mental Health Counselor",
            "company":     {"display_name": "Hartford Hospital"},
            "location":    {"display_name": "Hartford, CT"},
            "description": "We are looking for a licensed MHC...",
            "salary_min":  55000,
            "salary_max":  75000,
            "salary_is_predicted": "0",
            "redirect_url": "https://adzuna.com/jobs/abc123",
            "created":     "2026-07-01T09:00:00Z",
            "category":    {"label": "Healthcare & Nursing Jobs"},
        }
    ]
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID",  "test_id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test_key")
    return AdzunaClient()


@patch("src.lib.adzuna.requests.get")
def test_search_returns_normalized_jobs(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_RESPONSE
    mock_get.return_value           = mock_response

    jobs = client.search(what="mental health counselor", where="Connecticut")

    assert len(jobs) == 1
    assert jobs[0]["title"]               == "Mental Health Counselor"
    assert jobs[0]["company"]             == "Hartford Hospital"
    assert jobs[0]["salary_min"]          == 55000
    assert jobs[0]["salary_is_predicted"] == False


@patch("src.lib.adzuna.requests.get")
def test_search_handles_empty_results(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value           = mock_response

    jobs = client.search(what="mental health counselor")
    assert jobs == []


def test_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv("ADZUNA_APP_ID",  raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)

    with pytest.raises(ValueError):
        AdzunaClient()