$ScriptPath = "$PSScriptRoot\..\scripts\audit_pins.ps1"

Describe "audit_pins.ps1" {
    Context "When auditing a sketch file for GPIO safety" {
        It "Should return a JSON list containing pin safety violations" {
            $TestSketchPath = "$PSScriptRoot\temp_test_sketch.ino"
            
            # Create a mock sketch file containing unsafe pin settings:
            # - GPIO 6 (SPI Flash Pin) configured as OUTPUT
            # - GPIO 1 (TX0) configured as OUTPUT (disrupts serial programming/monitor)
            # - GPIO 2 (Normal pin) configured as OUTPUT (safe)
            $SketchCode = @"
void setup() {
  pinMode(6, OUTPUT);
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  digitalWrite(6, HIGH);
}
void loop() {}
"@
            $SketchCode | Out-File -FilePath $TestSketchPath -Encoding UTF8 -Force
            
            # Run the script
            $ResultJson = & $ScriptPath -SketchPath $TestSketchPath
            $Result = $ResultJson | ConvertFrom-Json
            
            # Assertions
            $Result.Count | Should Be 2
            
            $Result[0].Pin | Should Be 6
            $Result[0].Severity | Should Be "ERROR"
            $Result[0].Message | Should Match "SPI Flash Pin"
            
            $Result[1].Pin | Should Be 1
            $Result[1].Severity | Should Be "WARNING"
            $Result[1].Message | Should Match "Serial TX"
            
            # Clean up
            if (Test-Path $TestSketchPath) { Remove-Item $TestSketchPath -Force }
        }
    }
}
