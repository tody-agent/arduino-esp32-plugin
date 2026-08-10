$ServerPath = "$PSScriptRoot\..\..\..\mcp\mcp_server.py"
if (-not (Test-Path $ServerPath)) {
    $ServerPath = "C:\Users\block\Documents\antigravity\jolly-planck\esp32-master\mcp\mcp_server.py"
}

Describe "mcp_server.py (Simulation Tools)" {
    Context "When calling simulation tools via JSON-RPC" {
        It "Should handle start, status, and stop operations" {
            # Start Python process
            $pinfo = New-Object System.Diagnostics.ProcessStartInfo
            $pinfo.FileName = "python"
            $pinfo.Arguments = "-u `"$ServerPath`""
            $pinfo.RedirectStandardInput = $true
            $pinfo.RedirectStandardOutput = $true
            $pinfo.UseShellExecute = $false
            $pinfo.CreateNoWindow = $true
            
            $proc = New-Object System.Diagnostics.Process
            $proc.StartInfo = $pinfo
            [void]$proc.Start()
            
            # 1. Initialize
            $initReq = '{"jsonrpc":"2.0","method":"initialize","id":1}'
            $proc.StandardInput.WriteLine($initReq)
            $initRes = $proc.StandardOutput.ReadLine()
            $initRes | Should Match "arduino-esp32-mcp"
            
            # Create a mock sketch file
            $TestSketchPath = "$PSScriptRoot\temp_sim_sketch"
            if (-not (Test-Path $TestSketchPath)) { New-Item -ItemType Directory -Path $TestSketchPath -Force | Out-Null }
            $SketchCode = "void setup() { pinMode(2, OUTPUT); } void loop() { digitalWrite(2, HIGH); delay(100); }"
            $SketchCode | Out-File -FilePath "$TestSketchPath\temp_sim_sketch.ino" -Encoding UTF8 -Force
            
            # 2. Call start_simulation
            # Convert paths to forward slashes for python compatibility
            $TargetSketch = "$TestSketchPath\temp_sim_sketch.ino" -replace '\\', '/'
            $startReq = '{"jsonrpc":"2.0","method":"tools/call","id":2,"params":{"name":"start_simulation","arguments":{"sketch_path":"' + $TargetSketch + '"}}}'
            $proc.StandardInput.WriteLine($startReq)
            $startRes = $proc.StandardOutput.ReadLine()
            $startRes | Should Match "Simulation started successfully"
            
            # 3. Call get_simulation_status
            $statusReq = '{"jsonrpc":"2.0","method":"tools/call","id":3,"params":{"name":"get_simulation_status","arguments":{}}}'
            $proc.StandardInput.WriteLine($statusReq)
            $statusRes = $proc.StandardOutput.ReadLine()
            $statusRes | Should Match "RUNNING"
            
            # 4. Call stop_simulation
            $stopReq = '{"jsonrpc":"2.0","method":"tools/call","id":4,"params":{"name":"stop_simulation","arguments":{}}}'
            $proc.StandardInput.WriteLine($stopReq)
            $stopRes = $proc.StandardOutput.ReadLine()
            $stopRes | Should Match "Simulation stopped successfully"
            
            # 5. Verify status is STOPPED
            $proc.StandardInput.WriteLine($statusReq)
            $statusRes2 = $proc.StandardOutput.ReadLine()
            $statusRes2 | Should Match "STOPPED"
            
            # Clean up process
            $proc.StandardInput.Close()
            $proc.WaitForExit(1000)
            if (-not $proc.HasExited) { $proc.Kill() }
            
            # Clean up files
            if (Test-Path $TestSketchPath) { Remove-Item $TestSketchPath -Recurse -Force }
        }
    }
}
