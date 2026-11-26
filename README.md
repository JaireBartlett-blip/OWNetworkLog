# OWNetworkLog

A self-hosted network telemetry collector and match correlation logger built for **Overwatch** sessions. It continuously probes latency, jitter, packet loss, and DNS resolution in the background and links those real-time network metrics directly to logged competitive/quick-play matches.

---

## Features

- **Continuous 10-Second Telemetry Probe (`probe.py`):** Measures average ping, max latency spike, jitter, packet loss percentage, and DNS lookup time against Blizzard server endpoints using `mtr` and `dig`.
- **Live Web Dashboard (`app.py`):**
  - 5 real-time metric cards (*Current Avg Ping*, *Max Spike*, *Current Jitter*, *Packet Loss*, *DNS Lookup*).
  - Interactive **Chart.js** timeline plotting Avg Ping, Max Spike, and Jitter across the last 30 snapshots.
- **5-Second Match Logger & Built-In Match Timer:**
  - Single-button **Start / Stop Match Timer** tracks match duration using wall-clock timestamps (staying accurate even when a phone screen locks) and automatically tags logged matches (e.g., `[14m 32s]`).
  - Logs **Match Result** (`WIN` / `LOSS` / `DRAW`), **Role** (`TANK` / `DAMAGE` / `SUPPORT`), **Hero**, **Connection Feel**, and quick notes.
  - Correlates each match with average ping, peak spike, and packet loss during the match window.
- **Multi-Device LAN Access:** Accessible from a desktop browser or a phone on the local network for one-tap logging between games.

---

## Tech Stack

- **Backend:** Python 3, Flask, `mysql-connector-python`
- **Database:** MySQL / MariaDB (`overwatch_telemetry`)
- **Frontend:** Vanilla HTML/CSS/JavaScript, Chart.js
- **Telemetry Tools:** `mtr`, `dnsutils` (`dig`)
- **Deployment:** Ubuntu Linux VM with `systemd` background services (`ow-probe.service` & `ow-dashboard.service`)

---

## Project Structure

```text
OWNetworkLog/
├── app.py          # Flask web dashboard, REST API, & match logger UI
├── probe.py        # Background 10s network probe writing to MySQL
├── schema.sql      # Database schema (network_snapshots, match_sessions, match_logs)
├── .env.example    # Environment variable template for DB credentials & target host
└── README.md       # Project documentation
```

---

## Quick Setup

1. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL credentials and target game server IP
   ```

2. **Initialize the Database:**
   ```bash
   mysql -u root -p < schema.sql
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install flask mysql-connector-python
   ```

4. **Run Probe & Dashboard:**
   ```bash
   python3 probe.py &
   python3 app.py
   ```
   Open `http://localhost:5000` (or your host's LAN IP) in a browser.
