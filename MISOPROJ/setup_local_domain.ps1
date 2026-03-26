$domain = "MIS.Messaging.ph"
$ip = "192.168.20.10"
$hostsPath = "$env:windir\System32\drivers\etc\hosts"

$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host " [ERROR] PLEASE RUN AS ADMINISTRATOR " -ForegroundColor Red
    Pause
    exit
}

Write-Host "Stage 1: Domain Setup..."
$content = Get-Content $hostsPath -Raw
if ($content -match $domain) {
    $content = $content -replace ".*$domain.*`r?`n?", ""
    Set-Content -Path $hostsPath -Value $content
}
Add-Content -Path $hostsPath -Value "`r`n$ip       $domain"

Write-Host "Stage 2: Firewall Setup..."
Remove-NetFirewallRule -DisplayName "SMS_System_Port_80" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "SMS_System_Port_80" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow -Profile Any | Out-Null
Remove-NetFirewallRule -DisplayName "SMS_System_Port_5000" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "SMS_System_Port_5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Any | Out-Null

Write-Host "------------------------------------------------------------"
Write-Host " SUCCESS: SETUP COMPLETE" -ForegroundColor Green
Write-Host " Local URL: http://$domain"
Write-Host " Network URL: http://$ip:5000"
Write-Host "------------------------------------------------------------"
Pause
