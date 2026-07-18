# Define placeholders for Mocking in Pester 3
function Create-SerialPort {}

$ScriptPath = "$PSScriptRoot\..\scripts\serial_monitor.ps1"

Describe "serial_monitor.ps1" {
    Context "When monitoring a serial port" {
        It "Should read lines, write them to log, and support bidirectional serial queue transmission" {
            # Temp file paths
            $TestLogPath = "$PSScriptRoot\test_serial.log"
            $TestLockPath = "$PSScriptRoot\test_upload.lock"
            $TestQueuePath = "$PSScriptRoot\test_serial_input.queue"
            
            if (Test-Path $TestLogPath) { Remove-Item $TestLogPath -Force }
            if (Test-Path $TestLockPath) { Remove-Item $TestLockPath -Force }
            if (Test-Path $TestQueuePath) { Remove-Item $TestQueuePath -Force }
            
            # Setup mock port
            $mockPort = [PSCustomObject]@{
                IsOpen = $true
                PortName = "COM4"
                BaudRate = 115200
            }
            $mockPort | Add-Member -MemberType ScriptMethod -Name Open -Value { $this.IsOpen = $true }
            $mockPort | Add-Member -MemberType ScriptMethod -Name Close -Value { $this.IsOpen = $false }
            
            $global:transmittedData = @()
            $mockPort | Add-Member -MemberType ScriptMethod -Name Write -Value {
                param($data)
                $global:transmittedData += $data
            }
            
            $global:readCount = 0
            $mockPort | Add-Member -MemberType ScriptMethod -Name ReadLine -Value {
                $global:readCount++
                if ($global:readCount -eq 1) {
                    # Create queue file to simulate Agent sending data
                    "HELLO_ESP32" | Out-File -FilePath $TestQueuePath -Encoding UTF8 -Force
                    return "ESP32 Booting..."
                } elseif ($global:readCount -eq 2) {
                    # Create lock file to simulate upload start
                    New-Item -Path $TestLockPath -ItemType File -Force | Out-Null
                    return "Loop running"
                } elseif ($global:readCount -eq 3) {
                    # Delete lock file to simulate upload end
                    if (Test-Path $TestLockPath) { Remove-Item $TestLockPath -Force }
                    return "Resumed output"
                } else {
                    $this.IsOpen = $false
                    throw (New-Object System.IO.IOException "Simulated end of stream")
                }
            }
            
            # Mock Create-SerialPort helper
            Mock Create-SerialPort {
                param($PortName, $BaudRate)
                return $mockPort
            }
            
            # Run the monitor script
            $Result = . $ScriptPath -Port "COM4" -BaudRate 115200 -LogPath $TestLogPath -LockFile $TestLockPath -QueueFile $TestQueuePath -RunOnce -ErrorAction SilentlyContinue
            
            # Assertions
            Test-Path $TestLogPath | Should Be $true
            $LogLines = Get-Content $TestLogPath
            $LogLines.Count | Should BeGreaterThan 0
            $LogLines[0] | Should Match "ESP32 Booting..."
            
            # Bidirectional verification assertions:
            # 1. Queue file must be deleted by the script
            Test-Path $TestQueuePath | Should Be $false
            # 2. Port Write method must have received the queue data
            $global:transmittedData.Count | Should BeGreaterThan 0
            $global:transmittedData[0] | Should Match "HELLO_ESP32"
            
            # Cleanup
            if (Test-Path $TestLogPath) { Remove-Item $TestLogPath -Force }
            if (Test-Path $TestLockPath) { Remove-Item $TestLockPath -Force }
            if (Test-Path $TestQueuePath) { Remove-Item $TestQueuePath -Force }
        }
    }
}
