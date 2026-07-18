param(
    [string]$LogText,
    [string]$ElfPath,
    [string]$Addr2LinePath = ""
)

if (-not (Get-Command Find-Toolchain-Path -ErrorAction SilentlyContinue)) {
    function Find-Toolchain-Path {
        $arduino15Dir = Join-Path $env:LOCALAPPDATA "Arduino15"
        if (Test-Path $arduino15Dir) {
            $executables = Get-ChildItem -Path "$arduino15Dir\packages\esp32" -Filter "*elf-addr2line.exe" -Recurse -ErrorAction SilentlyContinue
            if ($executables) {
                $xtensa = $executables | Where-Object { $_.Name -like "xtensa*" } | Select-Object -First 1
                if ($xtensa) {
                    return $xtensa.FullName
                }
                return $executables[0].FullName
            }
        }
        
        $paths = "xtensa-esp32-elf-addr2line", "riscv32-esp-elf-addr2line", "xtensa-esp32-elf-addr2line.exe", "riscv32-esp-elf-addr2line.exe"
        foreach ($p in $paths) {
            $cmd = Get-Command $p -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        }
        
        return ""
    }
}

if (-not (Get-Command Invoke-Addr2Line -ErrorAction SilentlyContinue)) {
    function Invoke-Addr2Line {
        param(
            [string]$Addr2LinePath,
            [string]$ElfPath,
            [string[]]$Addresses
        )
        if (-not (Test-Path $ElfPath)) {
            Write-Warning "ELF file not found at $ElfPath"
            return $Addresses | ForEach-Object { "$($_): ELF file missing" }
        }
        if (-not $Addr2LinePath -or -not (Test-Path $Addr2LinePath)) {
            Write-Warning "addr2line compiler tool not found"
            return $Addresses | ForEach-Object { "$($_): addr2line missing" }
        }
        
        $args = @("-pfiaC", "-e", $ElfPath) + $Addresses
        & $Addr2LinePath @args
    }
}

if (-not $LogText) {
    Write-Error "LogText parameter is required."
    exit 1
}

$addresses = @()
if ($LogText -match 'Backtrace:\s*(.*)') {
    $btLine = $Matches[1]
    $pairs = $btLine -split '\s+'
    foreach ($pair in $pairs) {
        if ($pair -match '(0x[0-9a-fA-F]+):') {
            $addresses += $Matches[1]
        }
    }
}

if ($addresses.Count -eq 0) {
    $matches = [regex]::Matches($LogText, '0x40[0-9a-fA-F]{6}')
    foreach ($m in $matches) {
        $addresses += $m.Value
    }
    $addresses = $addresses | Select-Object -Unique
}

if ($addresses.Count -eq 0) {
    Write-Warning "No backtrace addresses found in log."
    return @()
}

if (-not $Addr2LinePath) {
    $Addr2LinePath = Find-Toolchain-Path
}

$decoded = Invoke-Addr2Line -Addr2LinePath $Addr2LinePath -ElfPath $ElfPath -Addresses $addresses
return $decoded
