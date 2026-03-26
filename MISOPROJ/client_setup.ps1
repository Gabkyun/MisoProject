$domain = "MIS.Messaging.ph"
$serverIp = "192.168.20.10" # This is the IP of your MAIN server computer
$hostsPath = "$env:windir\System32\drivers\etc\hosts"

Write-Host "--- CLIENT DOMAIN SETUP ---" -ForegroundColor Cyan
Write-Host "This will allow this PC to use http://$domain" -ForegroundColor White

# Check for Admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "[ERROR] PLEASE RUN THIS AS ADMINISTRATOR!" -ForegroundColor Red
    Write-Host "Right-click this file and 'Run with PowerShell' as Administrator." -ForegroundColor Yellow
    Pause
    exit
}

# Add to hosts
$content = Get-Content $hostsPath -Raw
if ($content -match $domain) {
    $content = $content -replace ".*$domain.*`r?`n?", ""
    Set-Content -Path $hostsPath -Value $content
}
Add-Content -Path $hostsPath -Value "`r`n$serverIp       $domain"

Write-Host "✅ SUCCESS!" -ForegroundColor Green
Write-Host "This computer can now access: http://$domain:5000" -ForegroundColor Cyan
Pause
