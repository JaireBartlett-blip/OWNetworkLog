# OWNetworkLog — Automated Network Telemetry & Hop Diagnostics Pipeline

A 24/7 Linux network observability daemon, relational MySQL time-series database, Discord webhook alerting engine, and Flask/Chart.js dashboard designed to diagnose ISP transit jitter, packet loss, and DNS resolution latency during live gameplay.

## Architecture
1. **Telemetry Probe (`probe.py` / `systemd`):** Executes automated ICMP/MTR path traces and DNS lookups every 10 seconds to measure RTT latency, jitter, packet loss, and worst-performing upstream router hops.
2. **Relational Time-Series Storage (`schema.sql` / MySQL):** Stores 10-second `network_snapshots`, `match_sessions`, and `match_logs` linked via foreign keys for root-cause fault isolation.
3. **Real-Time Alerting (Discord Webhooks):** Fires instant alerts when jitter or packet loss crosses configurable thresholds, identifying the degraded transit hop IP.
4. **Observability Dashboard (`app.py` / Flask + Chart.js):** Displays live KPIs, rolling latency/jitter timelines, and a 5-second match logger that correlates session outcomes with historical network telemetry.

## Quick Setup
1. Import `schema.sql` into MySQL and configure a local database user.
2. Copy `.env.example` to `.env` and fill in your MySQL credentials and Discord Webhook URL.
3. Run `probe.py` and `app.py` (or register them as `systemd` background services).
