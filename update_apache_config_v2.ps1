$path = "C:/xampp/apache/conf/httpd.conf"
$content = Get-Content $path -Raw

# Prepare the even better configuration blocks
$new_blocks = @"
<VirtualHost *:80>
    ServerName localhost
    ServerAlias 127.0.0.1 192.168.20.10
    DocumentRoot "C:/xampp/htdocs"
</VirtualHost>

<VirtualHost *:80>
    ServerName mis.messaging.ph
    ProxyPreserveHost On
    ProxyPass /phpmyadmin !
    ProxyPass /dashboard !
    ProxyPass /webalizer !
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
"@

# Regex to find the existing VirtualHost blocks we added
$old_blocks_regex = "(?s)<VirtualHost \*:80>\s*ServerName localhost.*?</VirtualHost>\s*<VirtualHost \*:80>\s*ServerName mis\.messaging\.ph.*?</VirtualHost>"

if ($content -match $old_blocks_regex) {
    Write-Host "Found existing VirtualHost blocks. Updating..."
    $content = $content -replace $old_blocks_regex, $new_blocks
} else {
    Write-Host "Could not find combined blocks, trying to find just the mis one..."
    $mis_regex = "(?s)<VirtualHost \*:80>\s*ServerName mis\.messaging\.ph.*?</VirtualHost>"
    if ($content -match $mis_regex) {
        $content = $content -replace $mis_regex, $new_blocks
    } else {
        Write-Error "Could not find any matching VirtualHost block to replace."
        exit 1
    }
}

Set-Content $path $content -Encoding UTF8
Write-Host "Success! Configuration updated with 127.0.0.1 and IP aliases."
