import os
import sys
import json
import time
import urllib.request
import subprocess

PORT = 8321

def test_dashboard():
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dashboard_path = os.path.join(scripts_dir, "scripts", "log_dashboard.py")
    
    print(f"Launching dashboard from {dashboard_path}...")
    proc = subprocess.Popen([sys.executable, dashboard_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)
    
    try:
        # Test GET /
        url_home = f"http://localhost:{PORT}/"
        req = urllib.request.urlopen(url_home)
        html_content = req.read().decode("utf-8")
        assert "ESP32 Mobile Studio" in html_content
        assert "window.showPage" in html_content
        print("[OK] GET / returned index page successfully.")

        # Test GET /api/status
        url_status = f"http://localhost:{PORT}/api/status"
        req_status = urllib.request.urlopen(url_status)
        status_json = json.loads(req_status.read().decode("utf-8"))
        assert "log_exists" in status_json
        print(f"[OK] GET /api/status returned: {status_json}")

        # Test GET /api/logs
        url_logs = f"http://localhost:{PORT}/api/logs?lines=10"
        req_logs = urllib.request.urlopen(url_logs)
        logs_json = json.loads(req_logs.read().decode("utf-8"))
        assert "lines" in logs_json
        print(f"[OK] GET /api/logs returned {len(logs_json['lines'])} lines.")

        # Test POST /api/send
        url_send = f"http://localhost:{PORT}/api/send"
        data = json.dumps({"data": "PING"}).encode("utf-8")
        req_send = urllib.request.Request(url_send, data=data, headers={"Content-Type": "application/json"})
        resp_send = urllib.request.urlopen(req_send)
        send_json = json.loads(resp_send.read().decode("utf-8"))
        assert send_json.get("status") == "ok"
        print("[OK] POST /api/send successfully transmitted queue data.")

        print("\nAll Dashboard tests PASSED cleanly!")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_dashboard()
