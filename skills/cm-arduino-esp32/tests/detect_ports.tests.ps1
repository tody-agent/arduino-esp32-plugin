$ScriptPath = "$PSScriptRoot\..\scripts\detect_ports.ps1"

Describe "detect_ports.ps1" {
    Context "When COM ports are connected" {
        It "Should return a JSON array containing connected ports" {
            # Mock Get-CimInstance to return a mock list of devices
            Mock Get-CimInstance {
                return @(
                    [PSCustomObject]@{
                        Caption = "Silicon Labs CP210x USB to UART Bridge (COM4)"
                        DeviceID = "USB\VID_10C4&PID_EA60\0001"
                    },
                    [PSCustomObject]@{
                        Caption = "Standard Serial over Bluetooth link (COM5)"
                        DeviceID = "BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}"
                    }
                )
            }
            
            # Run the script and parse output
            $ResultJson = & $ScriptPath
            $Result = $ResultJson | ConvertFrom-Json
            
            # Assertions
            $Result.Count | Should Be 2
            $Result[0].Port | Should Be "COM4"
            $Result[0].IsESP32 | Should Be $true
            $Result[1].Port | Should Be "COM5"
            $Result[1].IsESP32 | Should Be $false
        }
    }
}
