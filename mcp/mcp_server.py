import sys
import os
import json
import subprocess
import traceback
import re

# Determine directory paths relative to this script
mcp_dir = os.path.dirname(os.path.abspath(__file__))
plugin_root = os.path.dirname(mcp_dir)
scripts_dir = os.path.join(plugin_root, "skills", "cm-arduino-esp32", "scripts")

def log(msg):
    sys.stderr.write(f"[arduino-esp32-mcp] {msg}\n")
    sys.stderr.flush()

def run_powershell(script_name, args=[]):
    script_path = os.path.join(scripts_dir, script_name)
    if not os.path.exists(script_path):
        return {"error": f"Script not found at: {script_path}"}
    
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path] + args
    log(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

def run_cli_command(cmd_args):
    cmd = ["arduino-cli"] + cmd_args
    log(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

def load_cached_board_state():
    state_path = ".cm/board_state.json"
    if os.path.exists(state_path):
        try:
            with open(state_path, "r") as f:
                return json.load(f)
        except Exception as e:
            log(f"Warning: Failed to load cached board state: {e}")
    return {}

def parse_compiler_errors(stderr_text):
    diagnostics = []
    
    # 1. Missing header file check
    missing_header = re.search(r"fatal error:\s*(.*?\.h):\s*No such file or directory", stderr_text)
    if missing_header:
        header_name = missing_header.group(1)
        diagnostics.append({
            "type": "Missing Library",
            "header": header_name,
            "suggestion": f"Thiếu thư viện chứa header '{header_name}'. Hãy tìm kiếm và cài đặt thư viện này bằng lệnh `arduino-cli lib search` và `arduino-cli lib install`."
        })
    
    # 2. Sketch size too large check
    if "sketch too large" in stderr_text or "will not fit in region" in stderr_text:
        diagnostics.append({
            "type": "Sketch Too Large",
            "suggestion": "Kích thước chương trình vượt quá phân vùng ứng dụng của ESP32. Hãy cấu hình bảng phân vùng lớn hơn bằng cách thêm thuộc tính `--build-property build.partitions=huge_app` hoặc `--build-property build.partitions=no_ota` vào lệnh compile."
        })
        
    # 3. Specific line errors
    line_errors = re.findall(r"(.*?):(\d+):(\d+):\s*error:\s*(.*)", stderr_text)
    for err in line_errors[:5]:
        diagnostics.append({
            "type": "Syntax Error",
            "file": os.path.basename(err[0]),
            "line": int(err[1]),
            "column": int(err[2]),
            "message": err[3].strip()
        })
        
    return diagnostics

def handle_detect_ports():
    res = run_powershell("detect_ports.ps1")
    if "error" in res:
        return {"content": [{"type": "text", "text": f"Error running script: {res['error']}"}], "isError": True}
    
    # Try to cache detected port
    try:
        ports_list = json.loads(res["stdout"])
        if ports_list:
            default_port = None
            for p in ports_list:
                if p.get("IsESP32"):
                    default_port = p
                    break
            if not default_port:
                default_port = ports_list[0]
                
            os.makedirs(".cm", exist_ok=True)
            with open(".cm/board_state.json", "w") as sf:
                json.dump({
                    "port": default_port.get("Port"),
                    "name": default_port.get("Name"),
                    "fqbn": "esp32:esp32:esp32"
                }, sf)
            log(f"Cached default board state: {default_port.get('Port')}")
    except Exception as e:
        log(f"Warning: Failed to cache board state: {e}")
        
    return {"content": [{"type": "text", "text": res["stdout"]}]}

def handle_compile_sketch(sketch_path, fqbn=None, build_path=".cm/build"):
    cached = load_cached_board_state()
    target_fqbn = fqbn or cached.get("fqbn") or "esp32:esp32:esp32"
    
    abs_sketch = os.path.abspath(sketch_path)
    args = ["compile", "--fqbn", target_fqbn, "--build-path", build_path, "--build-cache-path", ".cm/build-cache", abs_sketch]
    res = run_cli_command(args)
    
    if "error" in res:
        return {"content": [{"type": "text", "text": f"Execution error: {res['error']}"}], "isError": True}
    
    is_failed = res["exit_code"] != 0
    diagnostics = []
    if is_failed:
        diagnostics = parse_compiler_errors(res["stderr"])
        
    result_dict = {
        "exit_code": res["exit_code"],
        "stdout": res["stdout"],
        "stderr": res["stderr"]
    }
    if diagnostics:
        result_dict["diagnostics"] = diagnostics
        
    return {
        "content": [{"type": "text", "text": json.dumps(result_dict, indent=2, ensure_ascii=False)}],
        "isError": is_failed
    }

def handle_upload_sketch(sketch_path, port=None, fqbn=None, lock_file=".cm/upload.lock"):
    cached = load_cached_board_state()
    target_port = port or cached.get("port")
    target_fqbn = fqbn or cached.get("fqbn") or "esp32:esp32:esp32"
    
    if not target_port:
        return {
            "content": [{"type": "text", "text": "Error: Port parameter was not provided and no cached board state was found. Please run detect_ports first or specify the port explicitly."}],
            "isError": True
        }
        
    lock_dir = os.path.dirname(lock_file)
    if lock_dir and not os.path.exists(lock_dir):
        os.makedirs(lock_dir, exist_ok=True)
        
    log("Creating upload lock file...")
    with open(lock_file, "w") as f:
        f.write("LOCK")
        
    abs_sketch = os.path.abspath(sketch_path)
    args = ["upload", "-p", target_port, "--fqbn", target_fqbn, abs_sketch]
    res = run_cli_command(args)
    
    log("Removing upload lock file...")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except Exception as e:
            log(f"Warning: Failed to remove lock file: {e}")
            
    if "error" in res:
        return {"content": [{"type": "text", "text": f"Execution error: {res['error']}"}], "isError": True}
        
    output = f"Exit code: {res['exit_code']}\n\nSTDOUT:\n{res['stdout']}\n\nSTDERR:\n{res['stderr']}"
    return {"content": [{"type": "text", "text": output}], "isError": res["exit_code"] != 0}

def handle_start_monitor(port=None, baud_rate=115200, log_path=".cm/esp32_serial.log", lock_file=".cm/upload.lock", queue_file=".cm/serial_input.queue"):
    cached = load_cached_board_state()
    target_port = port or cached.get("port")
    
    if not target_port:
        return {
            "content": [{"type": "text", "text": "Error: Port parameter was not provided and no cached board state was found."}],
            "isError": True
        }
        
    script_path = os.path.join(scripts_dir, "serial_monitor.ps1")
    if not os.path.exists(script_path):
        return {"content": [{"type": "text", "text": f"Monitor script not found"}], "isError": True}
        
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except Exception as e:
            log(f"Warning: Failed to clear old log: {e}")
            
    job_cmd = (
        f"Start-Job -Name Esp32Monitor -ScriptBlock {{ "
        f"powershell -NoProfile -ExecutionPolicy Bypass -File '{script_path}' "
        f"-Port '{target_port}' -BaudRate {baud_rate} -LogPath '{log_path}' -LockFile '{lock_file}' -QueueFile '{queue_file}' "
        f"}}"
    )
    log(f"Launching job: {job_cmd}")
    
    cmd = ["powershell", "-NoProfile", "-Command", job_cmd]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = f"Monitor started for {target_port} at {baud_rate} baud.\nJob info:\n{result.stdout}"
        return {"content": [{"type": "text", "text": output}], "isError": result.returncode != 0}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Failed to start monitor: {e}"}], "isError": True}

def handle_read_log(log_path=".cm/esp32_serial.log", lines_count=50):
    if not os.path.exists(log_path):
        return {"content": [{"type": "text", "text": f"Log file not found at {log_path}."}], "isError": True}
        
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        tail = lines[-lines_count:]
        return {"content": [{"type": "text", "text": "".join(tail)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Failed to read log: {e}"}], "isError": True}

def handle_decode_stack(log_text, elf_path, addr2line_path=""):
    args = ["-LogText", log_text, "-ElfPath", os.path.abspath(elf_path)]
    if addr2line_path:
        args += ["-Addr2LinePath", addr2line_path]
        
    res = run_powershell("decode_stack.ps1", args)
    if "error" in res:
        return {"content": [{"type": "text", "text": f"Error running decode: {res['error']}"}], "isError": True}
        
    return {"content": [{"type": "text", "text": res["stdout"]}]}

def handle_serial_send(data, queue_file=".cm/serial_input.queue"):
    q_dir = os.path.dirname(queue_file)
    if q_dir and not os.path.exists(q_dir):
        os.makedirs(q_dir, exist_ok=True)
        
    try:
        with open(queue_file, "w", encoding="utf-8") as f:
            f.write(data)
        return {"content": [{"type": "text", "text": f"Ghi thành công dữ liệu '{data}' vào hàng đợi truyền cổng Serial."}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Lỗi ghi hàng đợi: {e}"}], "isError": True}

def handle_audit_pins(sketch_path):
    res = run_powershell("audit_pins.ps1", ["-SketchPath", os.path.abspath(sketch_path)])
    if "error" in res:
        return {"content": [{"type": "text", "text": f"Error running pin audit: {res['error']}"}], "isError": True}
        
    return {"content": [{"type": "text", "text": res["stdout"]}]}

def handle_start_simulation(sketch_path):
    handle_stop_simulation()
    os.makedirs(".cm", exist_ok=True)
    
    log_path = ".cm/esp32_serial.log"
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except Exception as e:
            log(f"Warning: Failed to remove old serial log: {e}")
            
    simulator_script = os.path.join(scripts_dir, "arduino_simulator.py")
    if not os.path.exists(simulator_script):
        return {"content": [{"type": "text", "text": f"Simulator script not found at {simulator_script}."}], "isError": True}
        
    try:
        stdout_log = open(".cm/simulator_stdout.log", "w")
        stderr_log = open(".cm/simulator_stderr.log", "w")
        
        proc = subprocess.Popen(
            [sys.executable, simulator_script, os.path.abspath(sketch_path)],
            stdout=stdout_log,
            stderr=stderr_log,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        with open(".cm/simulator.pid", "w") as f:
            f.write(str(proc.pid))
            
        return {"content": [{"type": "text", "text": f"Simulation started successfully in background (PID: {proc.pid}). Output logged to .cm/esp32_serial.log."}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Failed to start simulation: {e}"}], "isError": True}

def handle_stop_simulation():
    pid_file = ".cm/simulator.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            log(f"Stopping simulation process with PID: {pid}")
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            else:
                import signal
                os.kill(pid, signal.SIGTERM)
            return {"content": [{"type": "text", "text": f"Simulation stopped successfully (PID: {pid})."}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Failed to stop simulation process: {e}"}], "isError": True}
        finally:
            try:
                os.remove(pid_file)
            except:
                pass
    return {"content": [{"type": "text", "text": "No active simulation process found."}]}

def handle_get_simulation_status():
    pid_file = ".cm/simulator.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            if sys.platform == "win32":
                res = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True)
                if str(pid) in res.stdout:
                    return {"content": [{"type": "text", "text": "RUNNING"}]}
            else:
                os.kill(pid, 0)
                return {"content": [{"type": "text", "text": "RUNNING"}]}
        except:
            pass
    return {"content": [{"type": "text", "text": "STOPPED"}]}

def main():
    log("Server starting...")
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line)
            method = request.get("method")
            req_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "arduino-esp32-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            elif method == "notifications/initialized":
                pass
                
            elif method == "tools/list":
                tools = [
                    {
                        "name": "detect_ports",
                        "description": "Quét cổng nối tiếp và tự động nhận diện thiết bị nạp ESP32, lưu cấu hình mặc định vào workspace.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "compile_sketch",
                        "description": "Biên dịch mã nguồn Arduino cho board ESP32 kèm phân tích lỗi biên dịch thông minh.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sketch_path": {"type": "string", "description": "Đường dẫn thư mục hoặc file sketch (.ino)"},
                                "fqbn": {"type": "string", "description": "Board FQBN (Tùy chọn, mặc định lấy từ cache hoặc esp32:esp32:esp32)"},
                                "build_path": {"type": "string", "description": "Thư mục build đầu ra (Mặc định: .cm/build)"}
                            },
                            "required": ["sketch_path"]
                        }
                    },
                    {
                        "name": "upload_sketch",
                        "description": "Nạp chương trình xuống board ESP32 qua Serial (tự động khóa/nhả monitor và lấy cổng mặc định từ cache).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sketch_path": {"type": "string", "description": "Đường dẫn thư mục hoặc file sketch"},
                                "port": {"type": "string", "description": "Cổng COM nạp code (Tùy chọn, mặc định lấy từ cache)"},
                                "fqbn": {"type": "string", "description": "Board FQBN (Tùy chọn, mặc định lấy từ cache)"},
                                "lock_file": {"type": "string", "description": "Đường dẫn file lock (Mặc định: .cm/upload.lock)"}
                            },
                            "required": ["sketch_path"]
                        }
                    },
                    {
                        "name": "start_serial_monitor",
                        "description": "Bắt đầu Job giám sát Serial ngầm ghi log ra file và hỗ trợ truyền cổng 2 chiều.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "port": {"type": "string", "description": "Cổng COM kết nối (Tùy chọn, mặc định lấy từ cache)"},
                                "baud_rate": {"type": "integer", "description": "Baudrate (Mặc định: 115200)"},
                                "log_path": {"type": "string", "description": "Đường dẫn lưu log file (Mặc định: .cm/esp32_serial.log)"},
                                "lock_file": {"type": "string", "description": "Đường dẫn file lock (Mặc định: .cm/upload.lock)"},
                                "queue_file": {"type": "string", "description": "Đường dẫn hàng đợi truyền serial (Mặc định: .cm/serial_input.queue)"}
                            }
                        }
                    },
                    {
                        "name": "read_serial_log",
                        "description": "Đọc N dòng cuối cùng của log Serial nối tiếp.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "log_path": {"type": "string", "description": "Đường dẫn log file (Mặc định: .cm/esp32_serial.log)"},
                                "lines_count": {"type": "integer", "description": "Số dòng cuối cần đọc (Mặc định: 50)"}
                            }
                        }
                    },
                    {
                        "name": "decode_crash_stack",
                        "description": "Giải mã Exception Backtrace lỗi crash ESP32 sang tệp/dòng code nguồn cụ thể.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "log_text": {"type": "string", "description": "Nội dung văn bản chứa stack trace lỗi crash"},
                                "elf_path": {"type": "string", "description": "Đường dẫn file build .elf trung gian"},
                                "addr2line_path": {"type": "string", "description": "Tùy chọn ghi đè đường dẫn addr2line"}
                            },
                            "required": ["log_text", "elf_path"]
                        }
                    },
                    {
                        "name": "serial_send",
                        "description": "Gửi chuỗi dữ liệu (lệnh điều khiển) xuống cổng Serial nối tiếp của ESP32 qua hàng đợi monitor.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "data": {"type": "string", "description": "Chuỗi dữ liệu cần gửi"},
                                "queue_file": {"type": "string", "description": "Tùy chọn tệp hàng đợi (Mặc định: .cm/serial_input.queue)"}
                            },
                            "required": ["data"]
                        }
                    },
                    {
                        "name": "audit_pins",
                        "description": "Quét và kiểm định mã nguồn để phát hiện việc sử dụng chân GPIO nguy hiểm hoặc gây crash trên ESP32.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sketch_path": {"type": "string", "description": "Đường dẫn thư mục chứa code sketch hoặc file .ino cần quét"}
                            },
                            "required": ["sketch_path"]
                        }
                    },
                    {
                        "name": "start_simulation",
                        "description": "Khởi chạy giả lập logic cục bộ chạy ẩn cho Sketch Arduino (không cần phần cứng).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sketch_path": {"type": "string", "description": "Đường dẫn thư mục chứa sketch hoặc file .ino"}
                            },
                            "required": ["sketch_path"]
                        }
                    },
                    {
                        "name": "stop_simulation",
                        "description": "Dừng tiến trình giả lập logic đang chạy ngầm.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "get_simulation_status",
                        "description": "Lấy trạng thái hoạt động của tiến trình giả lập (RUNNING hoặc STOPPED).",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": tools}
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                log(f"Calling tool: {tool_name} with args {arguments}")
                
                result = None
                if tool_name == "detect_ports":
                    result = handle_detect_ports()
                elif tool_name == "compile_sketch":
                    result = handle_compile_sketch(
                        arguments.get("sketch_path"),
                        arguments.get("fqbn"),
                        arguments.get("build_path", ".cm/build")
                    )
                elif tool_name == "upload_sketch":
                    result = handle_upload_sketch(
                        arguments.get("sketch_path"),
                        arguments.get("port"),
                        arguments.get("fqbn"),
                        arguments.get("lock_file", ".cm/upload.lock")
                    )
                elif tool_name == "start_serial_monitor":
                    result = handle_start_monitor(
                        arguments.get("port"),
                        arguments.get("baud_rate", 115200),
                        arguments.get("log_path", ".cm/esp32_serial.log"),
                        arguments.get("lock_file", ".cm/upload.lock"),
                        arguments.get("queue_file", ".cm/serial_input.queue")
                    )
                elif tool_name == "read_serial_log":
                    result = handle_read_log(
                        arguments.get("log_path", ".cm/esp32_serial.log"),
                        arguments.get("lines_count", 50)
                    )
                elif tool_name == "decode_crash_stack":
                    result = handle_decode_stack(
                        arguments.get("log_text"),
                        arguments.get("elf_path"),
                        arguments.get("addr2line_path", "")
                    )
                elif tool_name == "serial_send":
                    result = handle_serial_send(
                        arguments.get("data"),
                        arguments.get("queue_file", ".cm/serial_input.queue")
                    )
                elif tool_name == "audit_pins":
                    result = handle_audit_pins(
                        arguments.get("sketch_path")
                    )
                elif tool_name == "start_simulation":
                    result = handle_start_simulation(
                        arguments.get("sketch_path")
                    )
                elif tool_name == "stop_simulation":
                    result = handle_stop_simulation()
                elif tool_name == "get_simulation_status":
                    result = handle_get_simulation_status()
                else:
                    result = {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}], "isError": True}
                
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": result
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            else:
                if req_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    
        except Exception as e:
            log(f"Error handling request: {e}")
            log(traceback.format_exc())

if __name__ == "__main__":
    main()
