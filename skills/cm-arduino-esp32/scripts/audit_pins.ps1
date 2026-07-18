param(
    [string]$SketchPath
)

if (-not $SketchPath) {
    Write-Error "SketchPath parameter is required."
    exit 1
}

# Resolve target files to scan
$filesToScan = @()
if (Test-Path $SketchPath) {
    $item = Get-Item $SketchPath
    if ($item.PSIsContainer) {
        $filesToScan = Get-ChildItem -Path $SketchPath -Include "*.ino", "*.cpp", "*.h", "*.c" -Recurse -ErrorAction SilentlyContinue
    } else {
        $filesToScan = @($item)
    }
} else {
    Write-Error "Path does not exist: $SketchPath"
    exit 1
}

$violations = @()

# Predefined sensitive pins on ESP32
$sensitivePins = @{
    6 = @{ Severity = "ERROR"; Message = "SPI Flash Pin (CLK). Pin được nối trực tiếp với bộ nhớ SPI Flash của ESP32. Việc cấu hình làm OUTPUT sẽ gây crash chip lập tức." }
    7 = @{ Severity = "ERROR"; Message = "SPI Flash Pin (SD0). Pin được nối trực tiếp với bộ nhớ SPI Flash của ESP32. Việc cấu hình làm OUTPUT sẽ gây crash chip lập tức." }
    8 = @{ Severity = "ERROR"; Message = "SPI Flash Pin (SD1). Pin được nối trực tiếp với bộ nhớ SPI Flash của ESP32. Việc cấu hình làm OUTPUT sẽ gây crash chip lập tức." }
    9 = @{ Severity = "ERROR"; Message = "SPI Flash Pin (SD2). Pin được nối trực tiếp với bộ nhớ SPI Flash của ESP32. Việc cấu hình làm OUTPUT sẽ gây crash chip lập tức." }
    10 = @{ Severity = "ERROR"; Message = "SPI Flash Pin (SD3). Pin được nối trực tiếp với bộ nhớ SPI Flash của ESP32. Việc cấu hình làm OUTPUT sẽ gây crash chip lập tức." }
    11 = @{ Severity = "ERROR"; Message = "SPI Flash Pin (CMD). Pin được nối trực tiếp với bộ nhớ SPI Flash của ESP32. Việc cấu hình làm OUTPUT sẽ gây crash chip lập tức." }
    1 = @{ Severity = "WARNING"; Message = "Serial TX0 Pin. Chân truyền dữ liệu UART0 chính. Cấu hình làm OUTPUT có thể làm lỗi cổng truyền thông Serial Monitor và nạp chương trình." }
    3 = @{ Severity = "WARNING"; Message = "Serial RX0 Pin. Chân nhận dữ liệu UART0 chính. Cấu hình làm OUTPUT/INPUT có thể làm lỗi cổng truyền thông Serial Monitor và nạp chương trình." }
    0 = @{ Severity = "WARNING"; Message = "BOOT Pin (GPIO0). Chân cấu hình chế độ nạp chương trình. Sử dụng làm OUTPUT có thể làm lỗi khả năng reset vào chế độ bootloader của ESP32." }
}

foreach ($file in $filesToScan) {
    $lines = Get-Content -Path $file.FullName
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $lineText = $lines[$i]
        
        # 1. Scan for pinMode(X, OUTPUT)
        if ($lineText -match 'pinMode\s*\(\s*(\d+)\s*,\s*OUTPUT\s*\)') {
            $pin = [int]$Matches[1]
            if ($sensitivePins.ContainsKey($pin)) {
                $info = $sensitivePins[$pin]
                $violations += [PSCustomObject]@{
                    Pin      = $pin
                    Severity = $info.Severity
                    Message  = $info.Message
                    File     = $file.Name
                    Line     = $i + 1
                }
            }
        }
        
        # 2. Scan for digitalWrite(X, HIGH/LOW) on sensitive pins if they were driven
        # (For safety checking, let's keep it focus on pinMode since that triggers hardware driving)
    }
}

# Convert results to JSON
if ($violations.Count -gt 0) {
    $violations | ConvertTo-Json
} else {
    "[]"
}
