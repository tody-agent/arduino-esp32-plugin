$devices = @()
try {
    $devices = Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object { $_.Caption -match 'COM\d+' }
} catch {
    try {
        $devices = Get-WmiObject Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object { $_.Caption -match 'COM\d+' }
    } catch {}
}

$results = @()
if ($devices) {
    foreach ($dev in $devices) {
        if ($dev.Caption -match '\(COM(\d+)\)') {
            $port = "COM" + $Matches[1]
            $caption = $dev.Caption
            $deviceId = $dev.DeviceID
            
            # Check if this matches typical ESP32 drivers/VIDs
            $isEsp = ($caption -match "CP210" -or $caption -match "CH34" -or $caption -match "USB to UART" -or $caption -match "JTAG" -or $deviceId -match "VID_10C4" -or $deviceId -match "VID_1A86")
            
            $results += [PSCustomObject]@{
                Port = $port
                Name = $caption
                IsESP32 = [bool]$isEsp
            }
        }
    }
} else {
    try {
        $ports = [System.IO.Ports.SerialPort]::GetPortNames() | Select-Object -Unique
        foreach ($p in $ports) {
            $results += [PSCustomObject]@{
                Port = $p
                Name = "Generic Serial Port ($p)"
                IsESP32 = $false
            }
        }
    } catch {}
}

# Convert results to JSON
$results | ConvertTo-Json
