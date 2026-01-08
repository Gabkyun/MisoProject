$domain = "MIS.Messaging.ph"
$ip = "127.0.0.1"
$hostsPath = "$env:windir\System32\drivers\etc\hosts"

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "⚠️  Please run this script as Administrator to update the hosts file." -ForegroundColor Yellow
    exit
}

# Read existing hosts file
$content = Get-Content $hostsPath -Raw

if ($content -match $domain) {
    Write-Host "✅ Domain $domain is already configured in hosts file." -ForegroundColor Green
} else {
    try {
        Add-Content -Path $hostsPath -Value "`r`n$ip       $domain"
        Write-Host "✅ Successfully added $domain pointing to $ip" -ForegroundColor Green
        Write-Host "👉 You can now access the API at http://$domain (port 80 or 5000)" -ForegroundColor Cyan
    } catch {
        Write-Error "Failed to write to hosts file. Check permissions."
    }
}
