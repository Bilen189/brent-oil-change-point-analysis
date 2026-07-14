import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";

const API_BASE_URL = "http://127.0.0.1:5000/api";

function formatCurrency(value) {
  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(numericValue);
}

function formatPercentage(value) {
  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return "N/A";
  }

  return `${numericValue.toFixed(2)}%`;
}

function formatDate(value) {
  if (!value) {
    return "N/A";
  }

  const parsedDate = new Date(`${value}T00:00:00`);

  if (Number.isNaN(parsedDate.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(parsedDate);
}

function KpiCard({ label, value, detail }) {
  return (
    <article className="kpi-card">
      <p className="kpi-label">{label}</p>
      <h2 className="kpi-value">{value}</h2>
      <p className="kpi-detail">{detail}</p>
    </article>
  );
}

function LoadingScreen() {
  return (
    <main className="status-screen">
      <div className="loader" />
      <h1>Loading Brent oil analysis</h1>
      <p>Retrieving dashboard data from the Flask API...</p>
    </main>
  );
}

function ErrorScreen({ message, onRetry }) {
  return (
    <main className="status-screen">
      <div className="error-symbol">!</div>
      <h1>Dashboard data could not be loaded</h1>
      <p>{message}</p>
      <button type="button" onClick={onRetry}>
        Try again
      </button>
    </main>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  return (
    <div className="chart-tooltip">
      <strong>{formatDate(label)}</strong>
      <span>{formatCurrency(payload[0].value)} per barrel</span>
    </div>
  );
}

function toMonthEndDate(value) {
  if (!value) {
    return null;
  }

  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  const monthEnd = new Date(
    date.getFullYear(),
    date.getMonth() + 1,
    0,
  );

  return monthEnd.toISOString().slice(0, 10);
}

function App() {
  const [overview, setOverview] = useState(null);
  const [monthlyPrices, setMonthlyPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoint, setChangePoint] = useState(null);

  const [selectedEventId, setSelectedEventId] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [startDate, setStartDate] = useState("1987-05-20");
  const [endDate, setEndDate] = useState("2022-11-14");
  const [filteredPrices, setFilteredPrices] = useState([]);

  async function loadDashboardData() {
    setLoading(true);
    setErrorMessage("");

    try {
      const [
        overviewResponse,
        monthlyResponse,
        eventsResponse,
        changePointResponse,
      ] = await Promise.all([
        axios.get(`${API_BASE_URL}/overview`),
        axios.get(`${API_BASE_URL}/monthly-prices`),
        axios.get(`${API_BASE_URL}/events`),
        axios.get(`${API_BASE_URL}/change-point`),
      ]);

      setOverview(overviewResponse.data);
      setMonthlyPrices(monthlyResponse.data.data ?? []);
      setEvents(eventsResponse.data.data ?? []);
      setChangePoint(changePointResponse.data);
    } catch (error) {
      console.error("Dashboard API error:", error);

      const apiMessage = error.response?.data?.message;

      setErrorMessage(
        apiMessage ||
          "Confirm that the Flask server is running at http://127.0.0.1:5000.",
      );
    } finally {
      setLoading(false);
    }
  }

async function applyDateFilter() {
  setLoading(true);
  setErrorMessage("");

  try {
    const response = await axios.get(`${API_BASE_URL}/prices`, {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    });

    setFilteredPrices(response.data.data ?? []);
  } catch (error) {
    console.error("Date-filter API error:", error);

    const apiMessage = error.response?.data?.message;

    setErrorMessage(
      apiMessage ||
        "The selected date range could not be loaded.",
    );
  } finally {
    setLoading(false);
  }
}

useEffect(() => {
  let isMounted = true;

  async function fetchInitialDashboardData() {
    try {
      const [
        overviewResponse,
        monthlyResponse,
        eventsResponse,
        changePointResponse,
      ] = await Promise.all([
        axios.get(`${API_BASE_URL}/overview`),
        axios.get(`${API_BASE_URL}/monthly-prices`),
        axios.get(`${API_BASE_URL}/events`),
        axios.get(`${API_BASE_URL}/change-point`),
      ]);

      if (!isMounted) {
        return;
      }

      setOverview(overviewResponse.data);
      setMonthlyPrices(monthlyResponse.data.data ?? []);
      setEvents(eventsResponse.data.data ?? []);
      setChangePoint(changePointResponse.data);
    } catch (error) {
      console.error("Dashboard API error:", error);

      if (!isMounted) {
        return;
      }

      const apiMessage = error.response?.data?.message;

      setErrorMessage(
        apiMessage ||
          "Confirm that the Flask server is running at http://127.0.0.1:5000.",
      );
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
  }

  fetchInitialDashboardData();

  return () => {
    isMounted = false;
  };
}, []);

  const selectedEvent = useMemo(() => {
    return events.find(
      (event, index) =>
        `${event.event_date}-${index}` === selectedEventId,
    );
  }, [events, selectedEventId]);

  const changeMetrics = changePoint?.metrics ?? {};

const chartData = useMemo(() => {
  if (filteredPrices.length > 0) {
    return filteredPrices.map((record) => ({
      date: record.Date,
      price: Number(record.Price),
    }));
  }

  return monthlyPrices.map((record) => ({
    date: record.Date,
    price: Number(record.Monthly_Average_Price),
  }));
}, [filteredPrices, monthlyPrices]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (errorMessage) {
    return (
      <ErrorScreen
        message={errorMessage}
        onRetry={loadDashboardData}
      />
    );
  }

  return (
    <main className="dashboard">
      <header className="hero">
        <div>
          <p className="eyebrow">Birhan Energies · Market Intelligence</p>

          <h1>Brent Oil Change Point Dashboard</h1>

          <p className="hero-description">
            Explore historical Brent oil prices, Bayesian structural-break
            results and major geopolitical or economic events affecting the
            global energy market.
          </p>
        </div>

        <div className="hero-badge">
          <span className="status-dot" />
          Flask API connected
        </div>
      </header>

      <section className="kpi-grid" aria-label="Summary indicators">
        <KpiCard
          label="Historical observations"
          value={Number(
            overview?.observation_count ?? 0,
          ).toLocaleString()}
          detail="Daily records analyzed"
        />

        <KpiCard
          label="Average Brent price"
          value={formatCurrency(overview?.average_price)}
          detail="USD per barrel"
        />

        <KpiCard
          label="Detected change point"
          value={formatDate(overview?.change_point_date)}
          detail="Posterior median date"
        />

        <KpiCard
          label="Estimated mean increase"
          value={formatPercentage(overview?.percentage_change)}
          detail={`${formatCurrency(
            overview?.mean_before,
          )} → ${formatCurrency(overview?.mean_after)}`}
        />
      </section>

      <section className="content-grid">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Historical trend</p>
              <h2>Monthly Brent crude oil prices</h2>
              <p>
                The dashed marker represents the model’s dominant structural
                change point.
              </p>
            </div>

            <div className="chart-summary">
              <span>
                Minimum: {formatCurrency(overview?.minimum_price)}
              </span>
              <span>
                Maximum: {formatCurrency(overview?.maximum_price)}
              </span>
            </div>
          </div>
          

          <div className="filter-bar">
            <label>
              <span>Start date</span>
              <input
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </label>

            <label>
              <span>End date</span>
              <input
                type="date"
                value={endDate}
                onChange={(event) => setEndDate(event.target.value)}
              />
            </label>

            <button type="button" onClick={applyDateFilter}>
              Apply range
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setStartDate("1987-05-20");
                setEndDate("2022-11-14");
                setFilteredPrices([]);
              }}
            >
              Reset
            </button>
          </div>
      
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{
                  top: 20,
                  right: 25,
                  bottom: 15,
                  left: 5,
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#d7dee8"
                />

                <XAxis
                  dataKey="date"
                  minTickGap={55}
                  tickFormatter={(date) => date.slice(0, 4)}
                  stroke="#64748b"
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  stroke="#64748b"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `$${value}`}
                  width={58}
                />

                <Tooltip content={<CustomTooltip />} />

                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#0f766e"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 5 }}
                  name="Monthly average price"
                />

                {overview?.change_point_date && (
                  <ReferenceLine
                    x={overview.change_point_date}
                    stroke="#dc2626"
                    strokeWidth={2}
                    strokeDasharray="7 5"
                    label={{
                      value: "Change point",
                      position: "insideTopRight",
                      fill: "#991b1b",
                      fontSize: 12,
                    }}
                  />
                )}

                {selectedEvent?.event_date && (
                  <ReferenceLine
                    x={toMonthEndDate(selectedEvent.event_date)}
                    stroke="#d97706"
                    strokeWidth={2}
                    strokeDasharray="4 4"
                    label={{
                      value: selectedEvent.event_name,
                      position: "insideTopLeft",
                      fill: "#92400e",
                      fontSize: 11,
                    }}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>

        <aside className="panel model-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Bayesian model</p>
              <h2>Change point insight</h2>
            </div>
          </div>

          <div className="change-date">
            <span>Estimated structural break</span>
            <strong>
              {formatDate(
                changeMetrics.change_point_date_median ??
                  overview?.change_point_date,
              )}
            </strong>
          </div>

          <dl className="metric-list">
            <div>
              <dt>95% interval start</dt>
              <dd>
                {formatDate(
                  changeMetrics.change_point_date_hdi_lower,
                )}
              </dd>
            </div>

            <div>
              <dt>95% interval end</dt>
              <dd>
                {formatDate(
                  changeMetrics.change_point_date_hdi_upper,
                )}
              </dd>
            </div>

            <div>
              <dt>Mean before</dt>
              <dd>
                {formatCurrency(
                  changeMetrics.mean_before_median ??
                    overview?.mean_before,
                )}
              </dd>
            </div>

            <div>
              <dt>Mean after</dt>
              <dd>
                {formatCurrency(
                  changeMetrics.mean_after_median ??
                    overview?.mean_after,
                )}
              </dd>
            </div>

            <div>
              <dt>Absolute mean change</dt>
              <dd>
                {formatCurrency(
                  changeMetrics.absolute_mean_change,
                )}
              </dd>
            </div>

            <div>
              <dt>Probability of increase</dt>
              <dd>
                {changeMetrics.probability_mean_increased
                  ? formatPercentage(
                      Number(
                        changeMetrics.probability_mean_increased,
                      ) * 100,
                    )
                  : "N/A"}
              </dd>
            </div>
          </dl>

          <div className="model-note">
            <strong>Interpretation</strong>
            <p>
              The model identifies a dominant shift to a substantially higher
              average-price regime. It detects statistical association, not
              proof that one event caused the change.
            </p>
          </div>
        </aside>
      </section>

      <section className="panel event-panel">
        <div className="panel-heading event-heading">
          <div>
            <p className="section-label">Event exploration</p>
            <h2>Highlight a researched market event</h2>
            <p>
              Select an event to display its position on the historical price
              chart and review the expected market channel.
            </p>
          </div>

          <label className="event-selector">
            <span>Historical event</span>

            <select
              value={selectedEventId}
              onChange={(event) =>
                setSelectedEventId(event.target.value)
              }
            >
              <option value="">Select an event</option>

              {events.map((event, index) => {
                const eventId = `${event.event_date}-${index}`;

                return (
                  <option key={eventId} value={eventId}>
                    {event.event_date} — {event.event_name}
                  </option>
                );
              })}
            </select>
          </label>
        </div>

        {selectedEvent ? (
          <div className="event-detail-grid">
            <div>
              <span className="detail-label">Event</span>
              <strong>{selectedEvent.event_name}</strong>
            </div>

            <div>
              <span className="detail-label">Date</span>
              <strong>{formatDate(selectedEvent.event_date)}</strong>
            </div>

            <div>
              <span className="detail-label">Category</span>
              <strong>{selectedEvent.event_category}</strong>
            </div>

            <div>
              <span className="detail-label">Source</span>
              <strong>{selectedEvent.source_organization}</strong>
            </div>

            <div className="wide-detail">
              <span className="detail-label">Description</span>
              <p>{selectedEvent.event_description}</p>
            </div>

            <div className="wide-detail">
              <span className="detail-label">
                Expected market channel
              </span>
              <p>{selectedEvent.expected_market_channel}</p>
            </div>
          </div>
        ) : (
          <div className="empty-event">
            Select one of the {overview?.event_count ?? events.length} curated
            events to reveal its details.
          </div>
        )}
      </section>

      <footer>
        <p>
          Brent Oil Change Point Analysis · Bayesian results are presented
          with uncertainty and should not be interpreted as causal proof.
        </p>
      </footer>
    </main>
  );
}

export default App;