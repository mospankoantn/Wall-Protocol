param(
    [ValidateSet('PackageZip','Run','Build')][string]$Action='PackageZip',
    [string]$RuntimePath,
    [string]$UserPath
)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
if (-not $RuntimePath) {
    $runtimeFolders = @('GameMakerStudio2-LTS2026','GameMakerStudio2') | ForEach-Object {
        Get-ChildItem -LiteralPath (Join-Path $env:ProgramData "$_\Cache\runtimes") -Directory -ErrorAction SilentlyContinue
    }
    $candidate = $runtimeFolders | Where-Object { $_.Name -match '^runtime-\d+\.\d+\.\d+\.\d+$' } | Sort-Object { [version]($_.Name -replace '^runtime-','') } -Descending | Select-Object -First 1
    if(-not $candidate){throw 'Install a GameMaker Windows runtime or pass -RuntimePath.'}
    $RuntimePath=$candidate.FullName
}
if (-not $UserPath) {
    $profiles = @('GameMakerStudio2-LTS2026','GameMakerStudio2') | ForEach-Object {
        Get-ChildItem -LiteralPath (Join-Path $env:APPDATA $_) -Directory -ErrorAction SilentlyContinue
    }
    $profile=$profiles | Where-Object {$_.Name -match '_\d+$'} | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if(-not $profile){throw 'Open GameMaker once or pass -UserPath.'}
    $UserPath=$profile.FullName
}
$runtime=$RuntimePath
$buildDir=Join-Path $projectRoot 'build'
New-Item -ItemType Directory -Force -Path "$buildDir\package","$buildDir\cache","$buildDir\temp" | Out-Null
& "$runtime\bin\igor\windows\x64\Igor.exe" "--rp=$runtime" "--project=$projectRoot\Wall Protocol.yyp" "--user=$userPath" '--runtime=VM' "--cache=$buildDir\cache" "--temp=$buildDir\temp" "--of=$buildDir\package\WallProtocol.win" "--tf=$buildDir\WallProtocol.zip" windows $Action 2>&1 | Tee-Object -FilePath "$buildDir\compile.log"
if($LASTEXITCODE -ne 0){throw "GameMaker failed: $LASTEXITCODE. See build/compile.log"}
if($Action -eq 'PackageZip') {
    Copy-Item -LiteralPath "$projectRoot\docs\PLAY.md","$projectRoot\docs\ART.md" -Destination "$buildDir\package" -Force
    Compress-Archive -Path "$buildDir\package\Wall Protocol.exe","$buildDir\package\data.win","$buildDir\package\options.ini","$buildDir\package\PLAY.md","$buildDir\package\ART.md" -DestinationPath "$buildDir\WallProtocol.zip" -Force
}
