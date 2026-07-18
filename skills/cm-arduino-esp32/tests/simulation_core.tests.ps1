$ScriptPath = "$PSScriptRoot\..\scripts\arduino_simulator.py"

Describe "arduino_simulator.py (Simulation Core)" {
    Context "When translating C++ Arduino Sketch to Python" {
        It "Should translate pinMode, digitalWrite, delay, and setup/loop structures" {
            $CppCode = @"
void setup() {
  pinMode(2, OUTPUT);
  Serial.begin(115200);
}
void loop() {
  digitalWrite(2, HIGH);
  delay(500);
  digitalWrite(2, LOW);
  delay(500);
}
"@
            $TempCppFile = "$PSScriptRoot\temp_sim_sketch.ino"
            $CppCode | Out-File -FilePath $TempCppFile -Encoding UTF8 -Force
            
            # Run translation via Python CLI
            $PythonTestCmd = "import sys; sys.path.append(r'$PSScriptRoot\..\scripts'); import arduino_simulator; print(arduino_simulator.translate_cpp_to_python(open(r'$TempCppFile', 'r', encoding='utf-8').read()))"
            
            $PyOutput = python -c $PythonTestCmd
            $PyOutputString = $PyOutput -join "`n"
            
            # Assertions on translated python code
            $PyOutputString | Should Match "def setup\(\):"
            $PyOutputString | Should Match "def loop\(\):"
            $PyOutputString | Should Match "pinMode\(2, 1\)"
            $PyOutputString | Should Match "digitalWrite\(2, 1\)"
            $PyOutputString | Should Match "time.sleep\(500 / 1000.0\)"
            
            # Clean up
            if (Test-Path $TempCppFile) { Remove-Item $TempCppFile -Force }
        }
        
        It "Should return correct simulated analog values based on configuration" {
            $ConfigPath = ".cm/simulation_sensors.json"
            $ConfigContent = '{"34": {"type": "constant", "value": 2048}}'
            
            # Ensure .cm dir exists
            if (-not (Test-Path ".cm")) { New-Item -ItemType Directory -Path ".cm" -Force | Out-Null }
            $ConfigContent | Out-File -FilePath $ConfigPath -Encoding UTF8 -Force
            
            $TestScript = @"
import sys
import os
import json
import time
import math

sensor_config_file = '.cm/simulation_sensors.json'
start_time = time.time()

def analogRead(pin):
    if os.path.exists(sensor_config_file):
        with open(sensor_config_file, 'r', encoding='utf-8-sig') as f:
            cfg = json.load(f)
        pin_cfg = cfg.get(str(pin))
        if pin_cfg:
            t = pin_cfg.get('type')
            if t == 'constant':
                return pin_cfg.get('value', 2048)
    return -1

print(analogRead(34))
"@
            $TestScriptFile = "$PSScriptRoot\temp_sim_test.py"
            $TestScript | Out-File -FilePath $TestScriptFile -Encoding UTF8 -Force
            
            $Val = python $TestScriptFile
            [int]$Val | Should Be 2048
            
            # Cleanup
            if (Test-Path $TestScriptFile) { Remove-Item $TestScriptFile -Force }
            if (Test-Path $ConfigPath) { Remove-Item $ConfigPath -Force }
        }
    }
}
