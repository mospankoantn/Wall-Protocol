param([ValidateSet('PackageZip','Run','Build')][string]$Action='PackageZip')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$runtime='C:\ProgramData\GameMakerStudio2-LTS2026\Cache\runtimes\runtime-2026.0.0.23'
$userPath=Join-Path $env:APPDATA 'GameMakerStudio2\MospankoANTN_4302388'
$buildDir=Join-Path $projectRoot 'build'
New-Item -ItemType Directory -Force -Path "$buildDir\package","$buildDir\cache","$buildDir\temp" | Out-Null
& "$runtime\bin\igor\windows\x64\Igor.exe" "--rp=$runtime" "--project=$projectRoot\Wall Protocol.yyp" "--user=$userPath" '--runtime=VM' "--cache=$buildDir\cache" "--temp=$buildDir\temp" "--of=$buildDir\package\WallProtocol.win" "--tf=$buildDir\WallProtocol.zip" windows $Action 2>&1 | Tee-Object -FilePath "$buildDir\compile.log"
if($LASTEXITCODE -ne 0){throw "GameMaker failed: $LASTEXITCODE. See build/compile.log"}
