import os
import mysql.connector
from flask import Flask, request, jsonify, render_template_string

def load_env(path):
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "ow_monitor"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "overwatch_telemetry"),
}

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OWNetworkLog | Telemetry & Match Logger</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root { --bg: #0f172a; --card: #1e293b; --accent: #f97316; --text: #f8fafc; --muted: #94a3b8; --green: #22c55e; --red: #ef4444; --yellow: #eab308; }
    * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { margin: 0; background: var(--bg); color: var(--text); padding: 20px; }
    .container { max-width: 1100px; margin: 0 auto; }
    header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 12px; }
    h1 { margin: 0; font-size: 1.5rem; }
    h1 span { color: var(--accent); }
    .badge { background: #14532d; color: #86efac; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 20px; }
    .card { background: var(--card); border-radius: 12px; padding: 16px; border: 1px solid #334155; }
    .stat-label { color: var(--muted); font-size: 0.8rem; text-transform: uppercase; }
    .stat-val { font-size: 1.7rem; font-weight: 700; margin-top: 4px; }
    .two-col { display: grid; grid-template-columns: 1.4fr 1fr; gap: 18px; margin-bottom: 20px; }
    @media (max-width: 850px) { .two-col { grid-template-columns: 1fr; } }
    .btn-group { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 14px; }
    button.pill { background: #334155; color: var(--text); border: 2px solid transparent; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-weight: 600; }
    button.pill.active { border-color: var(--accent); background: #431407; color: #fdba74; }
    input { width: 100%; background: #0f172a; border: 1px solid #334155; color: var(--text); padding: 9px; border-radius: 8px; margin-top: 6px; margin-bottom: 12px; }
    button.submit { width: 100%; background: var(--accent); color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: 700; font-size: 1rem; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { text-align: left; padding: 10px; border-bottom: 1px solid #334155; }
    th { color: var(--muted); font-weight: 600; }
    .win { color: var(--green); font-weight: 700; }
    .loss { color: var(--red); font-weight: 700; }
    .draw { color: var(--yellow); font-weight: 700; }
  </style>
</head>
<body>
<div class="container">
  <header>
    <h1><span>OW</span>NetworkLog // Live Telemetry</h1>
    <div class="badge" id="live-status">◍ PROBE ACTIVE (10s)</div>
  </header>

  <div class="grid">
    <div class="card"><div class="stat-label">Current Avg Ping</div><div class="stat-val" id="m-ping">-- ms</div></div>
    <div class="card"><div class="stat-label">Max Spike (Last 30)</div><div class="stat-val" id="m-max">-- ms</div></div>
    <div class="card"><div class="stat-label">Current Jitter</div><div class="stat-val" id="m-jitter">-- ms</div></div>
    <div class="card"><div class="stat-label">Packet Loss</div><div class="stat-val" id="m-loss">-- %</div></div>
    <div class="card"><div class="stat-label">DNS Lookup</div><div class="stat-val" id="m-dns">-- ms</div></div>
  </div>

  <div class="two-col">
    <div class="card">
      <h3 style="margin-top:0;">Ping & Jitter Timeline (Last 30 Snapshots)</h3>
      <canvas id="netChart" height="150"></canvas>
    </div>

    <div class="card">
      <h3 style="margin-top:0;">5-Second Match Logger</h3>
      <div class="stat-label">Match Result</div>
      <div class="btn-group" data-field="result">
        <button type="button" class="pill active" data-val="WIN">WIN</button>
        <button type="button" class="pill" data-val="LOSS">LOSS</button>
        <button type="button" class="pill" data-val="DRAW">DRAW</button>
      </div>

      <div class="stat-label">Role Played</div>
      <div class="btn-group" data-field="role_played">
        <button type="button" class="pill" data-val="TANK">TANK</button>
        <button type="button" class="pill active" data-val="DAMAGE">DAMAGE</button>
        <button type="button" class="pill" data-val="SUPPORT">SUPPORT</button>
      </div>

      <div class="stat-label">Connection Feel</div>
      <div class="btn-group" data-field="connection_feel">
        <button type="button" class="pill active" data-val="SMOOTH">SMOOTH</button>
        <button type="button" class="pill" data-val="MINOR_LAG">MINOR LAG</button>
        <button type="button" class="pill" data-val="UNPLAYABLE">UNPLAYABLE</button>
      </div>

      <div class="stat-label">Hero & Quick Note (Optional)</div>
      <input type="text" id="hero_name" placeholder="Hero (e.g., Tracer, Ana, Winston)" />
      <input type="text" id="notes" placeholder="Notes (e.g., Rubber-banded in OT fight)" />
      
      <button type="button" class="submit" id="timer-btn" style="background:#2563eb; margin-bottom:10px;" onclick="toggleTimer()">Start Match Timer</button>
      <button class="submit" onclick="logMatch()">Log Match + Link Live Telemetry</button>
      <div id="save-msg" style="margin-top:8px; font-size:0.85rem; color:var(--green);"></div>
    </div>
  </div>

  <div class="card">
    <h3 style="margin-top:0;">Recent Logged Matches & Network Correlation</h3>
    <table>
      <thead>
        <tr><th>Time</th><th>Result</th><th>Role / Hero</th><th>Feel</th><th>Match Avg Ping</th><th>Max Spike</th><th>Packet Loss</th><th>Notes</th></tr>
      </thead>
      <tbody id="match-rows"></tbody>
    </table>
  </div>
</div>
<script>
const formState = { result: "WIN", role_played: "DAMAGE", connection_feel: "SMOOTH" };
document.querySelectorAll(".btn-group").forEach(group => {
  const field = group.dataset.field;
  group.querySelectorAll("button.pill").forEach(btn => {
    btn.addEventListener("click", () => {
      group.querySelectorAll("button.pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      formState[field] = btn.dataset.val;
    });
  });
});

const dsPing = { label: "Avg Ping (ms)", data: new Array(), borderColor: "#f97316", tension: 0.25 };
const dsSpike = { label: "Max Spike (ms)", data: new Array(), borderColor: "#ef4444", tension: 0.25 };
const dsJitter = { label: "Jitter (ms)", data: new Array(), borderColor: "#38bdf8", tension: 0.25 };

const netChart = new Chart(document.getElementById("netChart").getContext("2d"), {
  type: "line",
  data: { labels: new Array(), datasets: new Array(dsPing, dsSpike, dsJitter) },
  options: { responsive: true, scales: { y: { beginAtZero: true } } }
});

async function refreshTelemetry() {
  const res = await fetch("/api/telemetry");
  const data = await res.json();
  const matchBody = document.getElementById("match-rows");
  matchBody.innerHTML = (data.matches || []).map(m => `
    <tr>
      <td>${m.logged_at}</td>
      <td class="${m.result.toLowerCase()}">${m.result}</td>
      <td>${m.role_played || "-"} ${m.hero_name ? "(" + m.hero_name + ")" : ""}</td>
      <td>${m.connection_feel || "-"}</td>
      <td>${m.avg_ping ? m.avg_ping + " ms" : "--"}</td>
      <td>${m.max_ping ? m.max_ping + " ms" : "--"}</td>
      <td>${m.avg_loss !== null ? m.avg_loss + "%" : "--"}</td>
      <td>${m.notes || ""}</td>
    </tr>
  `).join("");

  if (!data.snapshots || !data.snapshots.length) return;

  const latest = data.snapshots[data.snapshots.length - 1];
  const maxRecent = Math.max(...data.snapshots.map(x => Number(x.max_ping_ms)));
  document.getElementById("m-ping").textContent = `${latest.avg_ping_ms} ms`;
  document.getElementById("m-max").textContent = `${maxRecent.toFixed(1)} ms`;
  document.getElementById("m-jitter").textContent = `${latest.jitter_ms} ms`;
  document.getElementById("m-loss").textContent = `${latest.packet_loss_pct} %`;
  document.getElementById("m-dns").textContent = `${latest.dns_lookup_ms} ms`;

  netChart.data.labels = data.snapshots.map(x => x.recorded_at.slice(11, 19));
  dsPing.data = data.snapshots.map(x => Number(x.avg_ping_ms));
  dsSpike.data = data.snapshots.map(x => Number(x.max_ping_ms));
  dsJitter.data = data.snapshots.map(x => Number(x.jitter_ms));
  netChart.update();
}

var matchStart = null, matchTimer = null, elapsedSec = 0;
function toggleTimer() {
  var btn = document.getElementById("timer-btn");
  if (!matchTimer) {
    if (!matchStart) { matchStart = Date.now(); elapsedSec = 0; }
    btn.style.background = "#16a34a";
    matchTimer = setInterval(function() {
      elapsedSec = Math.floor((Date.now() - matchStart) / 1000);
      btn.textContent = "Stop Timer (" + Math.floor(elapsedSec / 60) + "m " + (elapsedSec % 60) + "s)";
    }, 1000);
  } else {
    clearInterval(matchTimer); matchTimer = null;
    btn.style.background = "#475569";
    btn.textContent = "Recorded: " + Math.floor(elapsedSec / 60) + "m " + (elapsedSec % 60) + "s (Tap to resume)";
  }
}

async function logMatch() {
  if (matchTimer) toggleTimer();
  var noteInput = document.getElementById("notes");
  if (elapsedSec > 0) {
    noteInput.value = ("[" + Math.floor(elapsedSec / 60) + "m " + (elapsedSec % 60) + "s] " + noteInput.value).trim();
  }
  const payload = Object.assign({}, formState, {
    hero_name: document.getElementById("hero_name").value.trim(),
    notes: noteInput.value.trim(),
  });
  const res = await fetch("/api/matches", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    document.getElementById("hero_name").value = "";
    noteInput.value = "";
    matchStart = null; elapsedSec = 0;
    var tBtn = document.getElementById("timer-btn");
    tBtn.style.background = "#2563eb";
    tBtn.textContent = "Start Match Timer";
    const msg = document.getElementById("save-msg");
    msg.textContent = "Match logged & linked to live telemetry!";
    setTimeout(() => (msg.textContent = ""), 3500);
    refreshTelemetry();
  }
}


refreshTelemetry();
setInterval(refreshTelemetry, 10000);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/telemetry")
def get_telemetry():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT snapshot_id, CAST(recorded_at AS CHAR) AS recorded_at,
               avg_ping_ms, max_ping_ms, jitter_ms, packet_loss_pct, dns_lookup_ms
        FROM network_snapshots
        ORDER BY snapshot_id DESC LIMIT 30
    """)
    snapshots = list(reversed(cur.fetchall()))

    cur.execute("""
        SELECT m.match_id, CAST(m.logged_at AS CHAR) AS logged_at, m.result,
               m.role_played, m.hero_name, m.connection_feel, m.notes,
               ROUND(AVG(n.avg_ping_ms), 1) AS avg_ping,
               ROUND(MAX(n.max_ping_ms), 1) AS max_ping,
               ROUND(AVG(n.packet_loss_pct), 2) AS avg_loss
        FROM match_logs m
        LEFT JOIN match_sessions s ON m.session_id = s.session_id
        LEFT JOIN network_snapshots n ON n.session_id = s.session_id
        GROUP BY m.match_id
        ORDER BY m.match_id DESC LIMIT 15
    """)
    matches = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"snapshots": snapshots, "matches": matches})

@app.route("/api/matches", methods=["POST"])
def add_match():
    data = request.get_json() or {}
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO match_sessions (started_at, ended_at, duration_sec, server_ip)
        VALUES (NOW() - INTERVAL 10 MINUTE, NOW(), 600, %s)
    """, (os.getenv("TARGET_HOST", "24.105.62.129"),))
    session_id = cur.lastrowid

    cur.execute("""
        UPDATE network_snapshots
        SET session_id = %s
        WHERE session_id IS NULL AND recorded_at >= NOW() - INTERVAL 10 MINUTE
    """, (session_id,))

    cur.execute("""
        INSERT INTO match_logs (session_id, result, role_played, hero_name, connection_feel, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        session_id,
        data.get("result", "WIN"),
        data.get("role_played"),
        data.get("hero_name") or None,
        data.get("connection_feel"),
        data.get("notes") or None,
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "saved", "session_id": session_id}), 201

if __name__ == "__main__":
   
   app.run(host="0.0.0.0", port=5000)