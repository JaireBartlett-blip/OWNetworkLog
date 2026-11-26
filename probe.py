import os
import time
import json
import socket
import subprocess
import urllib.request
import mysql.connector

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "ow_monitor"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "overwatch_telemetry"),
}

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK", "")
TARGET_HOST = os.getenv("TARGET_HOST", "24.105.62.129")
TARGET_REGION = os.getenv("TARGET_REGION", "US-East")
PING_LIMIT = float(os.getenv("PING_THRESHOLD_MS", 75.0))
JITTER_LIMIT = float(os.getenv("JITTER_THRESHOLD_MS", 15.0))
LOSS_LIMIT = float(os.getenv("LOSS_THRESHOLD_PCT", 1.0))

last_alert_time = 0
ALERT_COOLDOWN_SEC = 60

def measure_dns(domain="us.actual.battle.net"):
    start = time.perf_counter()
    try:
        socket.gethostbyname(domain)
    except Exception:
        return 999.99
    return round((time.perf_counter() - start) * 1000, 2)

def run_mtr_probe(host):
    cmd = ["mtr", "--json", "-c", "5", "-i", "1", "-n", host]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    data = json.loads(result.stdout)
    hubs = data.get("report", {}).get("hubs", [])
    if not hubs:
        raise RuntimeError("No MTR hops returned")

    final_hop = hubs[-1]
    avg_ping = round(float(final_hop.get("Avg", 0)), 2)
    min_ping = round(float(final_hop.get("Best", 0)), 2)
    max_ping = round(float(final_hop.get("Wrst", 0)), 2)
    jitter = round(float(final_hop.get("Javg", final_hop.get("StDev", 0))), 2)
    loss_pct = round(float(final_hop.get("Loss%", 0)), 2)

    worst_hop_ip = None
    worst_hop_loss = 0.0
    for h in hubs:
        h_loss = float(h.get("Loss%", 0))
        if h.get("host") != "???" and h_loss >= worst_hop_loss:
            worst_hop_loss = round(h_loss, 2)
            worst_hop_ip = h.get("host")

    return avg_ping, min_ping, max_ping, jitter, loss_pct, worst_hop_ip, worst_hop_loss

def send_discord_alert(avg_ping, max_ping, jitter, loss_pct, worst_hop_ip):
    global last_alert_time
    if not WEBHOOK_URL or "://discord.com" not in WEBHOOK_URL:
        return
    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN_SEC:
        return
    last_alert_time = now

    payload = {
        "embeds": [{
            "title": f"⚠️ Overwatch Lag Spike Detected ({TARGET_REGION})",
            "color": 16358938,
            "fields": [
                {"name": "Avg / Max Ping", "value": f"{avg_ping} ms / {max_ping} ms", "inline": True},
                {"name": "Jitter", "value": f"{jitter} ms", "inline": True},
                {"name": "Packet Loss", "value": f"{loss_pct}%", "inline": True},
                {"name": "Worst Router Hop", "value": f"`{worst_hop_ip or 'N/A'}`", "inline": False}
            ]
        }]
    }
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"[Discord Error] {e}")

def main():
    print(f"Starting Overwatch Telemetry Probe -> {TARGET_HOST} ({TARGET_REGION})...")
    while True:
        try:
            dns_ms = measure_dns()
            avg_p, min_p, max_p, jitter, loss, worst_ip, worst_loss = run_mtr_probe(TARGET_HOST)
            alert = (avg_p > PING_LIMIT) or (jitter > JITTER_LIMIT) or (loss > LOSS_LIMIT)

            if alert:
                send_discord_alert(avg_p, max_p, jitter, loss, worst_ip)

            conn = mysql.connector.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO network_snapshots
                (target_region, avg_ping_ms, min_ping_ms, max_ping_ms, jitter_ms,
                 packet_loss_pct, dns_lookup_ms, worst_hop_ip, worst_hop_loss_pct, alert_triggered)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (TARGET_REGION, avg_p, min_p, max_p, jitter, loss, dns_ms, worst_ip, worst_loss, alert)
            )
            conn.commit()
            cur.close()
            conn.close()

            status = "ALERT SENT" if alert else "OK"
            print(f"[{status}] Ping: {avg_p}ms (max {max_p}ms) | Jitter: {jitter}ms | Loss: {loss}% | DNS: {dns_ms}ms | Hop: {worst_ip}")
        except Exception as e:
            print(f"[Probe Error] {e}")

        time.sleep(10)

if __name__ == "__main__":
    main()
