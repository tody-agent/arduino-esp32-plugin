import os
import sys
import re
import subprocess
import time

def translate_cpp_to_python(cpp_code):
    lines = cpp_code.split('\n')
    py_lines = [
        "import time",
        "import random",
        "import sys",
        "import os",
        "",
        "# Global variables and mock environments",
        "pins = {}",
        "pin_modes = {}",
        "serial_buffer = []",
        "serial_output_file = '.cm/esp32_serial.log'",
        "queue_file = '.cm/serial_input.queue'",
        "start_time = time.time()",
        "",
        "import math",
        "import json",
        "",
        "def pinMode(pin, mode):",
        "    pin_modes[pin] = mode",
        "    print(f'[SIM] Pin {pin} mode set to {mode}')",
        "",
        "def digitalWrite(pin, state):",
        "    pins[pin] = state",
        "    print(f'[SIM] Pin {pin} -> {state}')",
        "    log_serial(f'GPIO_{pin}:{state}')",
        "",
        "def digitalRead(pin):",
        "    return pins.get(pin, 0)",
        "",
        "def analogRead(pin):",
        "    sensor_config_file = '.cm/simulation_sensors.json'",
        "    if os.path.exists(sensor_config_file):",
        "        try:",
        "            with open(sensor_config_file, 'r', encoding='utf-8-sig') as f:",
        "                cfg = json.load(f)",
        "            pin_cfg = cfg.get(str(pin))",
        "            if pin_cfg:",
        "                t = pin_cfg.get('type')",
        "                if t == 'sine':",
        "                    mn = pin_cfg.get('min', 0)",
        "                    mx = pin_cfg.get('max', 4095)",
        "                    period = pin_cfg.get('period_seconds', 10)",
        "                    elapsed = time.time() - start_time",
        "                    return int(mn + (mx - mn) * (0.5 + 0.5 * math.sin(2 * math.pi * elapsed / period)))",
        "                elif t == 'constant':",
        "                    return pin_cfg.get('value', 2048)",
        "                elif t == 'random':",
        "                    mn = pin_cfg.get('min', 0)",
        "                    mx = pin_cfg.get('max', 4095)",
        "                    return random.randint(mn, mx)",
        "        except Exception as e:",
        "            print(f'[SIM Warning] Failed to read sensor config: {e}')",
        "    return random.randint(0, 4095)",
        "",
        "def log_serial(msg):",
        "    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')",
        "    try:",
        "        with open(serial_output_file, 'a', encoding='utf-8') as f:",
        "            f.write(f'[{timestamp}] {msg}\\n')",
        "    except:",
        "        pass",
        "",
        "def serial_print(msg):",
        "    sys.stdout.write(str(msg))",
        "    sys.stdout.flush()",
        "    log_serial(str(msg))",
        "",
        "def serial_println(msg=''):",
        "    print(msg)",
        "    log_serial(str(msg))",
        "",
        "class MockSerial:",
        "    def begin(self, baud):",
        "        print(f'[SIM] Serial initialized at {baud} baud.')",
        "    def print(self, msg):",
        "        serial_print(msg)",
        "    def println(self, msg=''):",
        "        serial_println(msg)",
        "    def available(self):",
        "        check_queue()",
        "        return len(serial_buffer)",
        "    def readStringUntil(self, terminator):",
        "        res = ''",
        "        while len(serial_buffer) > 0:",
        "            c = serial_buffer.pop(0)",
        "            if c == terminator:",
        "                break",
        "            res += c",
        "        return res",
        "    def read(self):",
        "        if len(serial_buffer) > 0:",
        "            return ord(serial_buffer.pop(0))",
        "        return -1",
        "",
        "Serial = MockSerial()",
        "",
        "def check_queue():",
        "    global serial_buffer",
        "    if os.path.exists(queue_file):",
        "        try:",
        "            with open(queue_file, 'r', encoding='utf-8-sig') as f:",
        "                content = f.read()",
        "            if content:",
        "                serial_buffer.extend(list(content))",
        "            os.remove(queue_file)",
        "        except:",
        "            pass",
        ""
    ]
    
    indent_level = 0
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
            
        # Skip comments
        if stripped.startswith("//"):
            py_lines.append("    " * indent_level + "# " + stripped[2:].strip())
            continue
            
        # Handle closing brace
        if stripped == "}":
            indent_level = max(0, indent_level - 1)
            continue
            
        clean = stripped
        if clean.endswith(";"):
            clean = clean[:-1]
            
        # Translate types/qualifiers (regex to match whole word only)
        clean = re.sub(r'\b(void|int|float|double|char|bool|String|const|unsigned)\b', '', clean).strip()
        
        # Basic replacements
        clean = clean.replace("true", "True").replace("false", "False")
        clean = clean.replace("HIGH", "1").replace("LOW", "0")
        clean = clean.replace("OUTPUT", "1").replace("INPUT", "0")
        
        # Translate delay
        if "delay(" in clean:
            clean = re.sub(r'delay\((.*?)\)', r'time.sleep(\1 / 1000.0)', clean)
            
        # Translate millis
        clean = clean.replace("millis()", "int((time.time() - start_time) * 1000)")
        
        # Translate functions
        if "setup()" in clean:
            clean = "def setup():"
        elif "loop()" in clean:
            clean = "def loop():"
            
        # Translate braces on control statements
        if clean.endswith("{"):
            clean = clean[:-1].strip() + ":"
            
        # Append line
        py_lines.append("    " * indent_level + clean)
        
        if stripped.endswith("{"):
            indent_level += 1
            
    py_lines.extend([
        "",
        "if __name__ == '__main__':",
        "    setup()",
        "    try:",
        "        while True:",
        "            loop()",
        "            time.sleep(0.001)",
        "    except KeyboardInterrupt:",
        "        print('[SIM] Simulation stopped.')"
    ])
    
    return "\n".join(py_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python arduino_simulator.py <sketch_path_or_file>")
        sys.exit(1)
        
    sketch_path = sys.argv[1]
    
    # Resolve single file
    target_file = None
    if os.path.isdir(sketch_path):
        # find .ino file
        for f in os.listdir(sketch_path):
            if f.endswith(".ino"):
                target_file = os.path.join(sketch_path, f)
                break
    elif os.path.isfile(sketch_path):
        target_file = sketch_path
        
    if not target_file or not os.path.exists(target_file):
        print(f"Error: Arduino sketch file not found at {sketch_path}")
        sys.exit(1)
        
    # Read sketch C++ code
    with open(target_file, "r", encoding="utf-8-sig") as f:
        cpp_code = f.read()
        
    # Translate
    print(f"[SIM] Translating C++ sketch {os.path.basename(target_file)} to Python...")
    py_code = translate_cpp_to_python(cpp_code)
    
    # Ensure .cm dir exists
    os.makedirs(".cm", exist_ok=True)
    run_file = ".cm/simulation_run.py"
    
    with open(run_file, "w", encoding="utf-8") as f:
        f.write(py_code)
        
    print(f"[SIM] Starting local logic simulation runner...")
    # Execute the python script
    try:
        proc = subprocess.run([sys.executable, run_file], check=False)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print("[SIM] Simulation terminated.")

if __name__ == "__main__":
    main()
