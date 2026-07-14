"""Tests for the Brent oil Flask API."""

from backend.app import create_app


def create_test_client():
    """Create a Flask test client."""

    app = create_app()
    app.config.update(TESTING=True)

    return app.test_client()


def test_health_endpoint():
    """The health endpoint should return a successful response."""

    client = create_test_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_overview_endpoint():
    """The overview endpoint should return dashboard indicators."""

    client = create_test_client()
    response = client.get("/api/overview")
    data = response.get_json()

    assert response.status_code == 200
    assert data["observation_count"] > 0
    assert data["event_count"] >= 10
    assert data["minimum_price"] < data["maximum_price"]


def test_prices_endpoint():
    """The price endpoint should return historical records."""

    client = create_test_client()
    response = client.get(
        "/api/prices"
        "?start_date=2020-01-01"
        "&end_date=2020-12-31"
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] > 0
    assert "Date" in data["data"][0]
    assert "Price" in data["data"][0]


def test_invalid_date_filter():
    """An invalid date query should return HTTP 400."""

    client = create_test_client()
    response = client.get(
        "/api/prices?start_date=not-a-date"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid request"


def test_change_point_endpoint():
    """The change-point endpoint should return model results."""

    client = create_test_client()
    response = client.get("/api/change-point")
    data = response.get_json()

    assert response.status_code == 200
    assert "metrics" in data
    assert "posterior_summary" in data


def test_events_endpoint():
    """The event endpoint should return the curated events."""

    client = create_test_client()
    response = client.get("/api/events")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] >= 10


def test_unknown_endpoint():
    """Unknown routes should return a structured 404 response."""

    client = create_test_client()
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Not found"

def test_monthly_prices_endpoint():
    """The monthly endpoint should return prepared monthly observations."""

    client = create_test_client()
    response = client.get("/api/monthly-prices")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] > 0
    assert "Date" in data["data"][0]
    assert "Monthly_Average_Price" in data["data"][0]


def test_event_association_endpoint():
    """The event-association endpoint should return modeled results."""

    client = create_test_client()
    response = client.get("/api/event-association")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] > 0
    assert "causality_notice" in data


def test_reversed_date_range():
    """A reversed date range should return HTTP 400."""

    client = create_test_client()
    response = client.get(
        "/api/prices"
        "?start_date=2021-01-01"
        "&end_date=2020-01-01"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid request"


def test_event_category_filter():
    """The event endpoint should support category filtering."""

    client = create_test_client()
    response = client.get("/api/events?category=OPEC")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] > 0

    for event in data["data"]:
        assert "opec" in event["event_category"].lower()