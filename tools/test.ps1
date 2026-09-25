param([int]$TimeoutSeconds=180)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$package=Join-Path $projectRoot 'build\package'
$testDir=Join-Path $env:LOCALAPPDATA 'Wall_Protocol'
$outputDir=Join-Path $projectRoot 'build\verification'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$started=Get-Date
$process=Start-Process -FilePath (Join-Path $package 'Wall Protocol.exe') -WorkingDirectory $package -ArgumentList '--wp-test' -PassThru -WindowStyle Hidden -RedirectStandardOutput "$outputDir\runner.log" -RedirectStandardError "$outputDir\runner-errors.log"
if(-not $process.WaitForExit($TimeoutSeconds*1000)) {throw "Test runner exceeded $TimeoutSeconds seconds; PID $($process.Id). Inspect the log."}
$resultFile=Join-Path $testDir 'wp_test_results.json'
if(-not(Test-Path -LiteralPath $resultFile)){throw 'No runtime result was written.'}
if((Get-Item -LiteralPath $resultFile).LastWriteTime -lt $started){throw 'Runtime result is stale; inspect the runner log.'}
$result=Get-Content -Raw -LiteralPath $resultFile | ConvertFrom-Json
Copy-Item -LiteralPath $resultFile -Destination "$outputDir\runtime-results.json" -Force
Get-ChildItem -LiteralPath $testDir -Filter 'wp_test_*.png' | Copy-Item -Destination $outputDir -Force
Write-Output $result.log
if(-not $result.passed){throw 'Runtime integration tests failed.'}
