# Define placeholders for Mocking in Pester 3
function Invoke-Addr2Line {}
function Find-Toolchain-Path {}

$ScriptPath = "$PSScriptRoot\..\scripts\decode_stack.ps1"

Describe "decode_stack.ps1" {
    Context "When given a backtrace" {
        It "Should extract addresses and decode them" {
            # Mock Invoke-Addr2Line helper
            Mock Invoke-Addr2Line {
                param($Addr2LinePath, $ElfPath, $Addresses)
                return @(
                    "0x400d0c35: setup() at C:\Users\block\Documents\antigravity\jolly-planck\MyProject/MyProject.ino:12",
                    "0x400d0c7a: loop() at C:\Users\block\Documents\antigravity\jolly-planck\MyProject/MyProject.ino:25"
                )
            }

            # Mock finding the toolchain path so it doesn't fail on missing local files
            Mock Find-Toolchain-Path {
                return "C:\mock\xtensa-esp32-elf-addr2line.exe"
            }

            # Mock Test-Path to simulate that the ElfPath and ToolchainPath exist
            Mock Test-Path {
                param($Path)
                if ($Path -like "*MyProject.ino.elf" -or $Path -like "*addr2line*") {
                    return $true
                }
                return $false
            }
            
            # Input log text
            $LogText = @"
Guru Meditation Error: Core  1 panic'ed (IntegerDivideByZero).
Backtrace:0x400d0c35:0x3ffb1f20 0x400d0c7a:0x3ffb1f40
"@
            
            # Dot-source the script so Pester's scope mocks are respected
            $Result = . $ScriptPath -LogText $LogText -ElfPath "C:\mock\build\MyProject.ino.elf" -Addr2LinePath "C:\mock\xtensa-esp32-elf-addr2line.exe"
            
            # Assertions
            $Result.Count | Should Be 2
            $Result[0] | Should Match "setup\(\) at .*ino:12"
            $Result[1] | Should Match "loop\(\) at .*ino:25"
        }
    }
}
