param(
    [string]$Port,
    [int]$BaudRate = 115200,
    [string]$LogPath = ".cm/esp32_serial.log",
    [string]$LockFile = ".cm/upload.lock",
    [string]$QueueFile = ".cm/serial_input.queue",
    [switch]$RunOnce
)

if (-not (Get-Command Create-SerialPort -ErrorAction SilentlyContinue)) {
    function Create-SerialPort {
        param($PortName, $BaudRate)
        [void][System.Reflection.Assembly]::LoadWithPartialName("System.IO.Ports")
        $port = New-Object System.IO.Ports.SerialPort $PortName, $BaudRate, None, 8, one
        $port.ReadTimeout = 1000
        return $port
    }
}

if (-not $Port) {
    Write-Error "Port parameter is required (e.g. COM4)."
    exit 1
}

$logDir = [System.IO.Path]::GetDirectoryName($LogPath)
if ($logDir -and -not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

Write-Host "Starting serial monitor on $Port ($BaudRate baud)..."
Write-Host "Logging to: $LogPath"
Write-Host "Lock file: $LockFile"
Write-Host "Queue file: $QueueFile"

$serialPort = $null
$running = $true

try {
    while ($running) {
        if (Test-Path $LockFile) {
            if ($serialPort -and $serialPort.IsOpen) {
                Write-Host "Upload lock file detected! Closing serial port temporarily..."
                $serialPort.Close()
            }
            Write-Host "Waiting for upload lock to be released..."
            while (Test-Path $LockFile) {
                Start-Sleep -Milliseconds 100
                if ($RunOnce) {
                    # Avoid infinite loop in tests
                    if (Test-Path $LockFile) {
                        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
                    }
                }
            }
            Write-Host "Upload finished, re-opening port..."
        }
        
        if (-not $serialPort -or -not $serialPort.IsOpen) {
            try {
                $serialPort = Create-SerialPort -PortName $Port -BaudRate $BaudRate
                $serialPort.Open()
                Write-Host "Serial port $Port opened successfully."
            } catch {
                Write-Warning "Failed to open serial port $Port. Retrying in 1s..."
                if ($RunOnce) {
                    $running = $false
                    break
                }
                Start-Sleep -Seconds 1
                continue
            }
        }

        # Check for bidirectional queue input
        if ($QueueFile -and (Test-Path $QueueFile)) {
            if ($serialPort -and $serialPort.IsOpen) {
                try {
                    $content = Get-Content -Path $QueueFile -Raw -ErrorAction SilentlyContinue
                    if ($content) {
                        Write-Host "Sending data to serial: $content"
                        $serialPort.Write($content)
                    }
                } catch {
                    Write-Warning "Failed to transmit queue data: $_"
                } finally {
                    Remove-Item -Path $QueueFile -Force -ErrorAction SilentlyContinue
                }
            }
        }
        
        try {
            $line = $serialPort.ReadLine()
            $line = $line -replace '\r|\n', ''
            
            Write-Host $line
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
            "[$timestamp] $line" | Out-File -FilePath $LogPath -Append -Encoding UTF8
        } catch [System.TimeoutException] {
            # normal timeout
        } catch {
            Write-Warning "Serial port disconnected or error: $($_.Exception.Message)"
            if ($serialPort) { $serialPort.Close() }
            
            if ($RunOnce) {
                $running = $false
            } else {
                Start-Sleep -Seconds 1
            }
        }
        
        if ($RunOnce -and -not $running) {
            break
        }
    }
} finally {
    if ($serialPort -and $serialPort.IsOpen) {
        $serialPort.Close()
        Write-Host "Serial port closed cleanly."
    }
}
