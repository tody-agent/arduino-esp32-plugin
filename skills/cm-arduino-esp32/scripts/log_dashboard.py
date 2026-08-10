#!/usr/bin/env python3
"""
ESP32 Log Studio - Mobile Companion Edition
Mobile-first, touch-friendly, intuitive Web UI for ESP32 hardware monitoring,
real-time log streaming, 1-click crash stack trace decoding, and smart repair guidance.
"""

import sys
import os
import json
import time
import subprocess
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = 8321
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SCRIPTS_DIR))
DEFAULT_LOG_PATH = ".cm/esp32_serial.log"
DEFAULT_LOCK_PATH = ".cm/upload.lock"
DEFAULT_QUEUE_PATH = ".cm/serial_input.queue"
DEFAULT_BUILD_DIR = ".cm/build"

def run_powershell(script_name, args=None):
    if args is None:
        args = []
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        return {"error": f"Script missing: {script_path}"}
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exit_code": res.returncode
        }
    except Exception as e:
        return {"error": str(e)}

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <title>ESP32 Mobile Studio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script>
        var currentLang = localStorage.getItem('esp32_lang') || 'en';

        var i18n = {
            en: {
                navStatus: "Status",
                navLogs: "Logs",
                navActions: "Actions",
                navRepair: "Smart Repair",
                demoBtn: "🚀 Try Demo",
                statusSmooth: "🟢 ESP32-S3 Running Smoothly!",
                statusCrash: "🔴 ESP32 Core Is Crashing!",
                statusSub: "COM3 Port • USB Serial CDC Active",
                cpuSpeed: "CPU Speed",
                freeRam: "Free RAM",
                btnLedOn: "LED ON",
                btnLedOff: "LED OFF",
                btnReboot: "Reboot",
                btnDecode: "Decode Crash",
                repairTitle: "💡 Smart Repair Assistant",
                repairNormal: "No hardware crash detected. ESP32-S3 microcontroller is functioning normally!",
                repairPanic: "⚠️ <b>Guru Meditation Error Detected!</b><br><br>Fix: Core panic caused by NULL pointer dereference. Inspect display/sensor initialization before accessing.",
                langBtn: "🌐 VI"
            },
            vi: {
                navStatus: "Trạng Thái",
                navLogs: "Nhật Ký",
                navActions: "Lệnh Nhanh",
                navRepair: "Trợ Lý Fix",
                demoBtn: "🚀 Thử Demo",
                statusSmooth: "🟢 ESP32-S3 Chạy Rất Smooth!",
                statusCrash: "🔴 Mạch Đang Bị Crash/Đơ!",
                statusSub: "Cổng COM3 • Kết nối USB Serial CDC Active",
                cpuSpeed: "Tốc Độ CPU",
                freeRam: "RAM Còn Trống",
                btnLedOn: "Bật LED",
                btnLedOff: "Tắt LED",
                btnReboot: "Reboot",
                btnDecode: "Decode Crash",
                repairTitle: "💡 Trợ Lý Sửa Lỗi Tự Động",
                repairNormal: "Hệ thống chưa phát hiện lỗi crash đơ mạch nào. Mạch ESP32-S3 đang vận hành hoàn toàn bình thường!",
                repairPanic: "⚠️ <b>Phát hiện lỗi Guru Meditation Error!</b><br><br>Khắc phục: Mạch bị đơ do cố ghi vào con trỏ NULL. Hãy kiểm tra các hàm hiển thị/cảm biến trước khi gọi.",
                langBtn: "🌐 EN"
            }
        };

        window.showPage = function(pageId) {
            console.log('Navigating to page:', pageId);
            var pages = document.getElementsByClassName('page');
            for (var i = 0; i < pages.length; i++) {
                pages[i].style.setProperty('display', 'none', 'important');
                pages[i].classList.remove('active');
            }
            var target = document.getElementById(pageId);
            if (target) {
                target.style.setProperty('display', 'flex', 'important');
                target.classList.add('active');
            }
            var navItems = document.getElementsByClassName('nav-item');
            for (var j = 0; j < navItems.length; j++) {
                navItems[j].classList.remove('active');
            }
            var activeBtns = document.querySelectorAll('[data-page="' + pageId + '"]');
            for (var k = 0; k < activeBtns.length; k++) {
                activeBtns[k].classList.add('active');
            }
        };

        window.toggleLang = function() {
            currentLang = currentLang === 'en' ? 'vi' : 'en';
            localStorage.setItem('esp32_lang', currentLang);
            window.applyLang();
            if (window.fetchLogs) window.fetchLogs();
        };

        window.applyLang = function() {
            var dict = i18n[currentLang] || i18n.en;
            document.querySelectorAll('.txt-nav-status').forEach(el => el.innerText = dict.navStatus);
            document.querySelectorAll('.txt-nav-logs').forEach(el => el.innerText = dict.navLogs);
            document.querySelectorAll('.txt-nav-actions').forEach(el => el.innerText = dict.navActions);
            document.querySelectorAll('.txt-nav-repair').forEach(el => el.innerText = dict.navRepair);
            
            var demoEl = document.getElementById('txt-demo-btn');
            if (demoEl) demoEl.innerText = dict.demoBtn;
            
            var langEl = document.getElementById('txt-lang-btn');
            if (langEl) langEl.innerText = dict.langBtn;
            
            var subEl = document.getElementById('heart-sub');
            if (subEl) subEl.innerText = dict.statusSub;
            
            var cpuEl = document.getElementById('txt-cpu-lbl');
            if (cpuEl) cpuEl.innerText = dict.cpuSpeed;
            
            var ramEl = document.getElementById('txt-ram-lbl');
            if (ramEl) ramEl.innerText = dict.freeRam;

            var lOn = document.getElementById('txt-btn-led-on');
            if (lOn) lOn.innerText = dict.btnLedOn;

            var lOff = document.getElementById('txt-btn-led-off');
            if (lOff) lOff.innerText = dict.btnLedOff;

            var lReb = document.getElementById('txt-btn-reboot');
            if (lReb) lReb.innerText = dict.btnReboot;

            var lDec = document.getElementById('txt-btn-decode');
            if (lDec) lDec.innerText = dict.btnDecode;

            var rHead = document.getElementById('txt-repair-head');
            if (rHead) rHead.innerText = dict.repairTitle;
        };

        window.sendCmd = function(cmd) {
            fetch('/api/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({data: cmd})
            }).then(function() { alert('Sent command: ' + cmd); });
        };

        window.loadDemoLogs = function() {
            fetch('/api/demo', {method: 'POST'})
                .then(function() { if (window.fetchLogs) window.fetchLogs(); });
        };

        window.triggerDecode = function() {
            fetch('/api/decode', {method: 'POST'})
                .then(function(r) { return r.json(); })
                .then(function(res) { alert('Decode Result:\n' + JSON.stringify(res, null, 2)); });
        };
    </script>
    <style>
        :root {
            --brand-accent: #00E5FF;
            --brand-accent-hover: #00B8D4;
            --mi-orange: #FF6900;
            --mi-bg: #0B0D12;
            --mi-card-bg: rgba(22, 25, 34, 0.85);
            --mi-card-border: rgba(255, 255, 255, 0.08);
            --mi-blue: #007AFF;
            --mi-green: #34C759;
            --mi-red: #FF3B30;
            --text-primary: #FFFFFF;
            --text-secondary: #9E9EA7;
            --terminal-bg: #07080B;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background: var(--mi-bg);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Top Header */
        header {
            height: 60px;
            background: rgba(18, 21, 29, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--mi-card-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            z-index: 100;
        }

        .brand-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-logo {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #00E5FF 0%, #FF6900 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            color: #FFF;
            font-size: 18px;
            box-shadow: 0 4px 14px rgba(0, 229, 255, 0.3);
        }

        .brand-title {
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: -0.3px;
        }

        .top-nav-desktop {
            display: flex;
            gap: 6px;
        }

        @media (max-width: 768px) {
            .top-nav-desktop {
                display: none !important;
            }
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header-btn {
            background: rgba(0, 229, 255, 0.12);
            border: 1px solid rgba(0, 229, 255, 0.35);
            color: var(--brand-accent);
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 700;
            min-height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Main Viewport Container */
        .viewport {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            padding-bottom: 90px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        /* Tab Content Pages */
        .page {
            display: none !important;
            flex-direction: column;
            gap: 16px;
        }

        .page.active {
            display: flex !important;
        }

        /* Card Component */
        .mi-card {
            background: var(--mi-card-bg);
            border: 1px solid var(--mi-card-border);
            border-radius: 24px;
            padding: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        /* Device Heartbeat Pulse Card */
        .heartbeat-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 14px;
            padding: 24px;
            background: linear-gradient(180deg, rgba(0, 229, 255, 0.06) 0%, rgba(22, 25, 34, 0.9) 100%);
            border: 1px solid rgba(0, 229, 255, 0.2);
        }

        .pulse-circle {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: rgba(52, 199, 89, 0.15);
            border: 2px solid var(--mi-green);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            position: relative;
            box-shadow: 0 0 20px rgba(52, 199, 89, 0.4);
        }

        .pulse-circle.error {
            background: rgba(255, 59, 48, 0.15);
            border-color: var(--mi-red);
            box-shadow: 0 0 20px rgba(255, 59, 48, 0.4);
        }

        .heartbeat-status {
            font-size: 1.15rem;
            font-weight: 800;
            color: #FFF;
        }

        .heartbeat-sub {
            font-size: 0.82rem;
            color: var(--text-secondary);
        }

        /* Metric Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .metric-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--mi-card-border);
            border-radius: 16px;
            padding: 14px;
            text-align: center;
        }

        .metric-val {
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--brand-accent);
        }

        .metric-lbl {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 2px;
        }

        /* Action Grid */
        .action-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
        }

        .touch-btn {
            background: var(--mi-card-bg);
            border: 1px solid var(--mi-card-border);
            border-radius: 20px;
            padding: 16px;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            cursor: pointer;
            transition: transform 0.15s ease, background 0.15s ease;
        }

        .touch-btn:active {
            transform: scale(0.95);
            background: rgba(0, 229, 255, 0.15);
        }

        .touch-btn-icon {
            font-size: 24px;
        }

        .touch-btn-label {
            font-size: 0.82rem;
            font-weight: 700;
            color: #FFF;
        }

        /* Log Terminal Area */
        .terminal-box {
            background: var(--terminal-bg);
            border: 1px solid var(--mi-card-border);
            border-radius: 20px;
            height: 420px;
            padding: 14px;
            overflow-y: auto;
            font-family: 'Fira Code', monospace;
            font-size: 0.84rem;
            line-height: 1.5;
        }

        .log-entry {
            margin-bottom: 4px;
            word-break: break-all;
        }
        .log-info { color: #60A5FA; }
        .log-warn { color: #FBBF24; }
        .log-panic { color: var(--mi-red); font-weight: 700; background: rgba(255,59,48,0.2); padding: 2px 6px; border-radius: 4px; }

        /* Floating Mobile Bottom Navigation Bar (Mobile First) */
        .bottom-nav {
            position: fixed;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 32px);
            max-width: 480px;
            height: 64px;
            background: rgba(22, 25, 34, 0.95);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 32px;
            display: flex;
            align-items: center;
            justify-content: space-around;
            padding: 0 10px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
            z-index: 9999;
            pointer-events: auto;
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 3px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 700;
            cursor: pointer !important;
            user-select: none;
            min-width: 64px;
            min-height: 48px;
            justify-content: center;
            border: none;
            background: transparent;
            transition: color 0.2s ease, transform 0.15s ease;
        }

        .nav-item * {
            pointer-events: none;
        }

        .nav-item.active {
            color: var(--brand-accent);
        }

        .nav-item:active {
            transform: scale(0.92);
        }

        .nav-icon {
            font-size: 20px;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="brand-group">
            <div class="brand-logo">⚡</div>
            <div class="brand-title">ESP32 Studio</div>
        </div>

        <div class="top-nav-desktop">
            <button class="nav-item active" data-page="page-status" onclick="window.showPage('page-status')">
                <span class="txt-nav-status">Status</span>
            </button>
            <button class="nav-item" data-page="page-logs" onclick="window.showPage('page-logs')">
                <span class="txt-nav-logs">Logs</span>
            </button>
            <button class="nav-item" data-page="page-actions" onclick="window.showPage('page-actions')">
                <span class="txt-nav-actions">Actions</span>
            </button>
            <button class="nav-item" data-page="page-repair" onclick="window.showPage('page-repair')">
                <span class="txt-nav-repair">Smart Repair</span>
            </button>
        </div>

        <div class="header-actions">
            <button class="header-btn" onclick="window.toggleLang()">
                <span id="txt-lang-btn">🌐 VI</span>
            </button>
            <button class="header-btn" onclick="window.loadDemoLogs()">
                <span id="txt-demo-btn">🚀 Try Demo</span>
            </button>
        </div>
    </header>

    <!-- Main Viewport -->
    <div class="viewport">

        <!-- PAGE 1: STATUS -->
        <div class="page active" id="page-status">
            <div class="mi-card heartbeat-card">
                <div class="pulse-circle" id="heart-circle">⚡</div>
                <div class="heartbeat-status" id="heart-status">🟢 ESP32-S3 Running Smoothly!</div>
                <div class="heartbeat-sub" id="heart-sub">COM3 Port • USB Serial CDC Active</div>
            </div>

            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-val">240 MHz</div>
                    <div class="metric-lbl" id="txt-cpu-lbl">CPU Speed</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">184 KB</div>
                    <div class="metric-lbl" id="txt-ram-lbl">Free RAM</div>
                </div>
            </div>
        </div>

        <!-- PAGE 2: LOG STREAM -->
        <div class="page" id="page-logs">
            <div class="terminal-box" id="terminal-box"></div>
        </div>

        <!-- PAGE 3: ACTIONS -->
        <div class="page" id="page-actions">
            <div class="action-grid">
                <div class="touch-btn" onclick="window.sendCmd('LED_ON')">
                    <div class="touch-btn-icon">💡</div>
                    <div class="touch-btn-label" id="txt-btn-led-on">LED ON</div>
                </div>
                <div class="touch-btn" onclick="window.sendCmd('LED_OFF')">
                    <div class="touch-btn-icon">🛑</div>
                    <div class="touch-btn-label" id="txt-btn-led-off">LED OFF</div>
                </div>
                <div class="touch-btn" onclick="window.sendCmd('REBOOT')">
                    <div class="touch-btn-icon">🔄</div>
                    <div class="touch-btn-label" id="txt-btn-reboot">Reboot</div>
                </div>
                <div class="touch-btn" onclick="window.triggerDecode()">
                    <div class="touch-btn-icon">🔍</div>
                    <div class="touch-btn-label" id="txt-btn-decode">Decode Crash</div>
                </div>
            </div>
        </div>

        <!-- PAGE 4: REPAIR ASSISTANT -->
        <div class="page" id="page-repair">
            <div class="mi-card">
                <h3 style="color: var(--brand-accent); margin-bottom: 10px;" id="txt-repair-head">💡 Smart Repair Assistant</h3>
                <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6;" id="repair-text">
                    No hardware crash detected. ESP32-S3 microcontroller is functioning normally!
                </p>
            </div>
        </div>

    </div>

    <!-- Floating Mobile Bottom Nav Bar -->
    <div class="bottom-nav">
        <button class="nav-item active" data-page="page-status" onclick="window.showPage('page-status')">
            <span class="nav-icon">🏠</span>
            <span class="txt-nav-status">Status</span>
        </button>
        <button class="nav-item" data-page="page-logs" onclick="window.showPage('page-logs')">
            <span class="nav-icon">📜</span>
            <span class="txt-nav-logs">Logs</span>
        </button>
        <button class="nav-item" data-page="page-actions" onclick="window.showPage('page-actions')">
            <span class="nav-icon">⚡</span>
            <span class="txt-nav-actions">Actions</span>
        </button>
        <button class="nav-item" data-page="page-repair" onclick="window.showPage('page-repair')">
            <span class="nav-icon">💡</span>
            <span class="txt-nav-repair">Smart Repair</span>
        </button>
    </div>

    <script>
        var logsData = [];

        window.fetchLogs = function() {
            fetch('/api/logs?lines=200')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    logsData = data.lines || [];
                    renderTerminal();
                })
                .catch(function(err) { console.error('Fetch logs error:', err); });
        };

        function renderTerminal() {
            var box = document.getElementById('terminal-box');
            if (!box) return;
            var html = '';
            var hasPanic = false;

            logsData.forEach(function(line) {
                var css = 'log-info';
                var low = line.toLowerCase();
                if (low.includes('guru meditation') || low.includes('panic') || low.includes('backtrace:')) {
                    css = 'log-panic';
                    hasPanic = true;
                } else if (low.includes('warn') || low.includes('warning')) {
                    css = 'log-warn';
                }

                html += '<div class="log-entry ' + css + '">' + escapeHtml(line) + '</div>';
            });

            box.innerHTML = html;
            box.scrollTop = box.scrollHeight;

            var statusText = document.getElementById('heart-status');
            var statusCircle = document.getElementById('heart-circle');
            var repairText = document.getElementById('repair-text');
            var dict = i18n[currentLang] || i18n.en;

            if (hasPanic) {
                if (statusText) statusText.innerText = dict.statusCrash;
                if (statusCircle) statusCircle.className = 'pulse-circle error';
                if (repairText) repairText.innerHTML = dict.repairPanic;
            } else {
                if (statusText) statusText.innerText = dict.statusSmooth;
                if (statusCircle) statusCircle.className = 'pulse-circle';
                if (repairText) repairText.innerHTML = dict.repairNormal;
            }
        }

        function escapeHtml(t) {
            return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        document.addEventListener('DOMContentLoaded', function() {
            window.applyLang();
            var btns = document.querySelectorAll('.nav-item');
            btns.forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    var targetPage = btn.getAttribute('data-page');
                    if (targetPage) {
                        window.showPage(targetPage);
                    }
                });
            });
        });

        setInterval(window.fetchLogs, 1000);
        window.fetchLogs();
    </script>
</body>
</html>
"""

class DashboardRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif path == "/api/status":
            log_exists = os.path.exists(DEFAULT_LOG_PATH)
            lock_active = os.path.exists(DEFAULT_LOCK_PATH)
            self._send_json({"log_exists": log_exists, "lock_active": lock_active, "port": "COM3"})

        elif path == "/api/logs":
            lines_count = int(query.get("lines", [200])[0])
            log_lines = []
            if os.path.exists(DEFAULT_LOG_PATH):
                try:
                    with open(DEFAULT_LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
                        log_lines = [l.strip() for l in f.readlines()[-lines_count:]]
                except Exception as e:
                    log_lines = [f"[Error reading log: {e}]"]
            self._send_json({"lines": log_lines})

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else ""
        data = json.loads(body) if body else {}

        if path == "/api/send":
            cmd_text = data.get("data", "").strip()
            if cmd_text:
                queue_dir = os.path.dirname(DEFAULT_QUEUE_PATH)
                if queue_dir and not os.path.exists(queue_dir):
                    os.makedirs(queue_dir, exist_ok=True)
                with open(DEFAULT_QUEUE_PATH, "w", encoding="utf-8") as f:
                    f.write(cmd_text + "\n")
                self._send_json({"status": "ok", "sent": cmd_text})
            else:
                self._send_json({"status": "error", "message": "Empty command"})

        elif path == "/api/demo":
            demo_lines = [
                "[2026-08-10 20:36:00.100] [INFO] ESP32-S3 Mobile Studio Boot: v0.2",
                "[2026-08-10 20:36:00.150] [INFO] CPU Frequency: 240 MHz, Flash Mode: QIO 80MHz",
                "[2026-08-10 20:36:01.000] [INFO] Initializing FreeRTOS multi-core tasks...",
                "[2026-08-10 20:36:01.500] [INFO] ADC Pin GPIO 4 Read: 2410 (Voltage = 1.94V)",
                "[2026-08-10 20:36:02.100] [WARNING] Memory High-watermark warning: Task 'SensorTask' stack remaining: 256 bytes",
                "[2026-08-10 20:36:02.500] [INFO] Serial Queue Executed: LED_ON",
                "[2026-08-10 20:36:03.000] [ERROR] Null pointer dereference in Task 'DisplayTask'!",
                "[2026-08-10 20:36:03.005] Guru Meditation Error: Core 1 panic'ed (StoreProhibited). Exception was not handled.",
                "[2026-08-10 20:36:03.010] Backtrace: 0x400d1254:0x3ffb1f20 0x400d13e0:0x3ffb1f40 0x400d0f12:0x3ffb1f60"
            ]
            os.makedirs(os.path.dirname(DEFAULT_LOG_PATH), exist_ok=True)
            with open(DEFAULT_LOG_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(demo_lines) + "\n")
            self._send_json({"status": "demo_loaded"})

        elif path == "/api/decode":
            elf_file = None
            if os.path.exists(DEFAULT_BUILD_DIR):
                for fname in os.listdir(DEFAULT_BUILD_DIR):
                    if fname.endswith(".elf"):
                        elf_file = os.path.join(DEFAULT_BUILD_DIR, fname)
                        break

            log_text = ""
            if os.path.exists(DEFAULT_LOG_PATH):
                with open(DEFAULT_LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
                    log_text = f.read()

            if not elf_file:
                self._send_json({"error": "Không tìm thấy file .elf"})
                return

            res = run_powershell("decode_stack.ps1", ["-LogText", log_text, "-ElfPath", elf_file])
            decoded = [l.strip() for l in res.get("stdout", "").splitlines() if l.strip()]
            self._send_json({"decoded": decoded})

        else:
            self.send_error(404, "Not Found")

    def _send_json(self, obj):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

def start_server():
    server = HTTPServer(("0.0.0.0", PORT), DashboardRequestHandler)
    print(f"ESP32 Mobile Studio running on http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
