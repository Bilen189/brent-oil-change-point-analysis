"""Flask API for the Brent oil change-point dashboard."""

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from backend.data_service import (
        DataServiceError,
        build_overview,
        load_change_point_results,
        load_event_association,
        load_events,
        load_historical_prices,
        load_monthly_prices,
    )
except ModuleNotFoundError:
    from data_service import (
        DataServiceError,
        build_overview,
        load_change_point_results,
        load_event_association,
        load_events,
        load_historical_prices,
        load_monthly_prices,
    )


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            }
        },
    )

    @app.get("/")
    def home():
        """Return basic API information."""

        return jsonify(
            {
                "name": "Brent Oil Change Point API",
                "status": "running",
                "version": "1.0.0",
                "documentation": "/api",
            }
        )

    @app.get("/api")
    def api_documentation():
        """Return the available API endpoints."""

        return jsonify(
            {
                "endpoints": {
                    "overview": "/api/overview",
                    "historical_prices": (
                        "/api/prices?start_date=YYYY-MM-DD"
                        "&end_date=YYYY-MM-DD"
                    ),
                    "monthly_prices": "/api/monthly-prices",
                    "change_point_results": "/api/change-point",
                    "events": "/api/events?category=<category>",
                    "event_association": "/api/event-association",
                    "health": "/api/health",
                }
            }
        )

    @app.get("/api/health")
    def health():
        """Return an API health response."""

        return jsonify(
            {
                "status": "healthy",
                "service": "brent-oil-dashboard-api",
            }
        )

    @app.get("/api/overview")
    def overview():
        """Return dashboard summary indicators."""

        return jsonify(build_overview())

    @app.get("/api/prices")
    def historical_prices():
        """Return historical daily price data."""

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        data = load_historical_prices(
            start_date=start_date,
            end_date=end_date,
        )

        return jsonify(
            {
                "count": len(data),
                "start_date": start_date,
                "end_date": end_date,
                "data": data,
            }
        )

    @app.get("/api/monthly-prices")
    def monthly_prices():
        """Return monthly average Brent prices."""

        data = load_monthly_prices()

        return jsonify(
            {
                "count": len(data),
                "data": data,
            }
        )

    @app.get("/api/change-point")
    def change_point():
        """Return Bayesian change-point model results."""

        return jsonify(load_change_point_results())

    @app.get("/api/events")
    def events():
        """Return historical events."""

        category = request.args.get("category")
        data = load_events(category=category)

        return jsonify(
            {
                "count": len(data),
                "category": category,
                "data": data,
            }
        )

    @app.get("/api/event-association")
    def event_association():
        """Return modeled event-association results."""

        data = load_event_association()

        return jsonify(
            {
                "count": len(data),
                "data": data,
                "causality_notice": (
                    "Temporal proximity does not establish causal impact."
                ),
            }
        )

    @app.errorhandler(ValueError)
    def handle_validation_error(error):
        """Handle invalid query parameters."""

        return (
            jsonify(
                {
                    "error": "Invalid request",
                    "message": str(error),
                }
            ),
            400,
        )

    @app.errorhandler(DataServiceError)
    def handle_data_error(error):
        """Handle missing or invalid data files."""

        return (
            jsonify(
                {
                    "error": "Data service error",
                    "message": str(error),
                }
            ),
            500,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):
        """Handle unknown routes."""

        return (
            jsonify(
                {
                    "error": "Not found",
                    "message": "The requested API endpoint does not exist.",
                }
            ),
            404,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )