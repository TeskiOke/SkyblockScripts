# HYPIXEL PING MONITOR
$trials = 5

function Get-PingSummary {
    param($server, $count = 5)
    Write-Host "`n--- Testing latency to ${server} ($count packets) ---" -ForegroundColor Cyan
    $results = 1..$count | ForEach-Object {
        try {
            # Using -Count 1 to get individual response times
            $ping = Test-Connection -ComputerName $server -Count 1 -ErrorAction Stop
            $ms = $ping.ResponseTime
            $color = if ($ms -lt 150) { "Green" } elseif ($ms -lt 250) { "Yellow" } else { "Red" }
            Write-Host "Address ${server}: time=$ms ms" -ForegroundColor $color
            $ms
        }
        catch {
            Write-Host "Packet to ${server} lost" -ForegroundColor Red
            $null
        }
        Start-Sleep -Milliseconds 200
    }
    $validResults = $results | Where-Object { $_ -ne $null }
    if ($validResults.Count -gt 0) {
        $avg = ($validResults | Measure-Object -Average).Average
        Write-Host "Average ping to ${server}: $([math]::Round($avg, 2)) ms" -ForegroundColor Magenta
        return $avg
    }
    return $null
}

Clear-Host
Write-Host "HYPIXEL LATENCY ANALYSIS" -ForegroundColor White -BackgroundColor Blue
Write-Host "Note: 40-50ms is usually the entry node (Cloudflare), not the actual US game server." -ForegroundColor Gray

$proxyPing = Get-PingSummary "proxy.hypixel.net" $trials
$mainPing = Get-PingSummary "mc.hypixel.net" $trials

Write-Host "`n=== FINAL VERDICT ===" -ForegroundColor Cyan
if ($null -ne $proxyPing -and $null -ne $mainPing) {
    if ($proxyPing -lt $mainPing) {
        Write-Host "Address 'proxy.hypixel.net' is $([math]::Round($mainPing - $proxyPing, 0)) ms faster." -ForegroundColor Green
        Write-Host "RECOMMENDATION: Use proxy.hypixel.net for entry." -ForegroundColor Yellow
    }
    else {
        Write-Host "No significant difference or main server is faster." -ForegroundColor Green
        Write-Host "RECOMMENDATION: Use mc.hypixel.net." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Could not complete tests for one or both addresses." -ForegroundColor Red
}

Write-Host "`nPress Enter to exit..."
Read-Host
