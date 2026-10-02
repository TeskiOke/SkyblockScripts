param(
  [Parameter(Mandatory = $false)]
  [string[]] $Roots = @($env:USERPROFILE),

  [Parameter(Mandatory = $false)]
  [switch] $AllLocalDrives,

  [Parameter(Mandatory = $false)]
  [ValidateRange(1, 10000)]
  [int] $TopFiles = 80,

  [Parameter(Mandatory = $false)]
  [ValidateRange(1, 10000)]
  [int] $TopDirs = 30,

  [Parameter(Mandatory = $false)]
  [ValidateRange(1, 10)]
  [int] $DirDepth = 2,

  [Parameter(Mandatory = $false)]
  [ValidateRange(1, 1000)]
  [int] $TopExtensions = 20,

  [Parameter(Mandatory = $false)]
  [ValidateRange(0, 1000000)]
  [int] $MinFileSizeMB = 200,

  [Parameter(Mandatory = $false)]
  [ValidateRange(0, 1000000)]
  [int] $SummaryMinFileSizeMB = 1,

  [Parameter(Mandatory = $false)]
  [ValidateRange(100, 200000)]
  [int] $ProgressUpdateEveryFiles = 4000,

  [Parameter(Mandatory = $false)]
  [string] $OutDir = (Join-Path $env:USERPROFILE "Desktop\Audit")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ToLiteralPath {
  param([Parameter(Mandatory = $true)][string] $PathLike)
  try {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($PathLike)
  } catch {
    return $PathLike
  }
}

function Format-Bytes {
  param([Parameter(Mandatory = $true)][long] $Bytes)
  if ($Bytes -ge 1TB) { return ("{0:N2} TB" -f ($Bytes / 1TB)) }
  if ($Bytes -ge 1GB) { return ("{0:N2} GB" -f ($Bytes / 1GB)) }
  if ($Bytes -ge 1MB) { return ("{0:N2} MB" -f ($Bytes / 1MB)) }
  if ($Bytes -ge 1KB) { return ("{0:N2} KB" -f ($Bytes / 1KB)) }
  return ("{0} B" -f $Bytes)
}

$rootDriveRegex = '^[A-Za-z]:\\$'
function Get-DriveRootFromPath {
  param([Parameter(Mandatory = $true)][string] $PathLike)
  $p = Resolve-ToLiteralPath -PathLike $PathLike
  try { $p = [System.IO.Path]::GetFullPath($p) } catch { }
  if ($p.Length -ge 3 -and $p[1] -eq ':' -and ($p[2] -eq '\' -or $p[2] -eq '/')) {
    return ($p.Substring(0, 3) -replace '/', '\')
  }
  return $null
}

function Get-DirBucket {
  param(
    [Parameter(Mandatory = $true)][string] $FileFullName,
    [Parameter(Mandatory = $true)][string] $RootLiteral,
    [Parameter(Mandatory = $true)][int] $Depth
  )

  $rootFull = $RootLiteral
  try { $rootFull = [System.IO.Path]::GetFullPath($RootLiteral) } catch { }
  if (-not $rootFull.EndsWith('\')) { $rootFull = $rootFull + '\' }

  $dir = [System.IO.Path]::GetDirectoryName($FileFullName)
  if (-not $dir) { return $rootFull.TrimEnd('\') }

  $dirFull = $dir
  try { $dirFull = [System.IO.Path]::GetFullPath($dir) } catch { }

  if ($dirFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    $rel = $dirFull.Substring($rootFull.Length)
    if ([string]::IsNullOrWhiteSpace($rel)) { return $rootFull.TrimEnd('\') }
    $parts = $rel -split '[\\/]+'
    $take = [Math]::Min($Depth, $parts.Length)
    if ($take -le 0) { return $rootFull.TrimEnd('\') }
    $bucketRel = ($parts[0..($take - 1)] -join '\')
    return (Join-Path ($rootFull.TrimEnd('\')) $bucketRel)
  }

  return $dirFull
}

$runStarted = Get-Date
$outDirLiteral = Resolve-ToLiteralPath -PathLike $OutDir
New-Item -ItemType Directory -Path $outDirLiteral -Force | Out-Null

$logPath = Join-Path $outDirLiteral "run.log"
"Disk audit started: $runStarted" | Out-File -FilePath $logPath -Encoding UTF8
"AllLocalDrives: $AllLocalDrives" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"Roots: $($Roots -join '; ')" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"TopFiles: $TopFiles" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"MinFileSizeMB: $MinFileSizeMB" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"TopDirs: $TopDirs" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"DirDepth: $DirDepth" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"TopExtensions: $TopExtensions" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"SummaryMinFileSizeMB: $SummaryMinFileSizeMB" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"ProgressUpdateEveryFiles: $ProgressUpdateEveryFiles" | Out-File -FilePath $logPath -Encoding UTF8 -Append

if ($AllLocalDrives) {
  $Roots = @(
    Get-PSDrive -PSProvider FileSystem |
      Where-Object { $_.Root -match $rootDriveRegex } |
      Select-Object -ExpandProperty Root
  )
}

$minBytesLarge = [long]$MinFileSizeMB * 1MB
$minBytesSummary = [long]$SummaryMinFileSizeMB * 1MB

$allLargeFiles = New-Object System.Collections.Generic.List[object]
$dirTotals = @{}
$dirCounts = @{}
$extTotals = @{}
$extCounts = @{}

$errors = 0
$processed = 0L
$foundLarge = 0L

$driveRoots = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($r in $Roots) {
  $dr = Get-DriveRootFromPath -PathLike $r
  if ($dr) { [void]$driveRoots.Add($dr) }
}
$driveSummary = @()
foreach ($dr in ($driveRoots | Sort-Object)) {
  try {
    $psd = Get-PSDrive -Name $dr.Substring(0,1) -PSProvider FileSystem -ErrorAction Stop
    $used = [long]$psd.Used
    $free = [long]$psd.Free
    $total = $used + $free
    $pct = if ($total -gt 0) { [math]::Round(($used / $total) * 100, 2) } else { 0 }
    $driveSummary += [pscustomobject]@{
      Drive      = $dr
      UsedBytes  = $used
      FreeBytes  = $free
      TotalBytes = $total
      UsedPct    = $pct
    }
  } catch { }
}

Write-Progress -Id 1 -Activity "Disk audit" -Status "Starting..." -PercentComplete 0

foreach ($root in $Roots) {
  $rootLiteral = Resolve-ToLiteralPath -PathLike $root
  "Scanning: $rootLiteral" | Out-File -FilePath $logPath -Encoding UTF8 -Append

  try {
    if (-not (Test-Path -LiteralPath $rootLiteral)) {
      "  SKIP (not found): $rootLiteral" | Out-File -FilePath $logPath -Encoding UTF8 -Append
      continue
    }

    # Access denied is common; we keep going by using SilentlyContinue here.
    Get-ChildItem -LiteralPath $rootLiteral -Recurse -File -Force -ErrorAction SilentlyContinue |
      ForEach-Object {
        $processed++
        $len = [long]$_.Length

        if ($ProgressUpdateEveryFiles -gt 0 -and ($processed % $ProgressUpdateEveryFiles) -eq 0) {
          $status = "Processed: $processed files | Large found: $foundLarge | Current: $($_.FullName)"
          Write-Progress -Id 1 -Activity "Disk audit" -Status $status
        }

        if ($len -ge $minBytesSummary) {
          $bucket = Get-DirBucket -FileFullName $_.FullName -RootLiteral $rootLiteral -Depth $DirDepth

          if (-not $dirTotals.ContainsKey($bucket)) { $dirTotals[$bucket] = 0L; $dirCounts[$bucket] = 0L }
          $dirTotals[$bucket] = [long]$dirTotals[$bucket] + $len
          $dirCounts[$bucket] = [long]$dirCounts[$bucket] + 1L

          $ext = $_.Extension
          if ([string]::IsNullOrWhiteSpace($ext)) { $ext = "<noext>" }
          $ext = $ext.ToLowerInvariant()
          if (-not $extTotals.ContainsKey($ext)) { $extTotals[$ext] = 0L; $extCounts[$ext] = 0L }
          $extTotals[$ext] = [long]$extTotals[$ext] + $len
          $extCounts[$ext] = [long]$extCounts[$ext] + 1L
        }

        if ($len -ge $minBytesLarge) {
          $foundLarge++
          $allLargeFiles.Add([pscustomobject]@{
            Root             = $rootLiteral
            FullName         = $_.FullName
            Name             = $_.Name
            Extension        = $_.Extension
            LengthBytes      = $len
            SizeMB           = [math]::Round($len / 1MB, 2)
            LastWriteTimeUtc = $_.LastWriteTimeUtc
          }) | Out-Null
        }
      }
  } catch {
    $errors++
    "  ERROR: $($_.Exception.Message)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
  }
}

Write-Progress -Id 1 -Activity "Disk audit" -Completed

$top = $allLargeFiles |
  Sort-Object -Property LengthBytes -Descending |
  Select-Object -First $TopFiles

$csvPath = Join-Path $outDirLiteral "top-files.csv"
$jsonPath = Join-Path $outDirLiteral "top-files.json"
$dirCsvPath = Join-Path $outDirLiteral "top-dirs.csv"
$extCsvPath = Join-Path $outDirLiteral "ext-summary.csv"
$driveCsvPath = Join-Path $outDirLiteral "drive-summary.csv"
$txtPath = Join-Path $outDirLiteral "summary.txt"

$top | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
$top | ConvertTo-Json -Depth 6 | Out-File -FilePath $jsonPath -Encoding UTF8

$topDirsResult = $dirTotals.Keys |
  ForEach-Object {
    [pscustomobject]@{
      Bucket      = $_
      TotalBytes  = [long]$dirTotals[$_]
      TotalSize   = (Format-Bytes -Bytes ([long]$dirTotals[$_]))
      FileCount   = [long]$dirCounts[$_]
    }
  } |
  Sort-Object -Property TotalBytes -Descending |
  Select-Object -First $TopDirs

$topExtResult = $extTotals.Keys |
  ForEach-Object {
    [pscustomobject]@{
      Extension   = $_
      TotalBytes  = [long]$extTotals[$_]
      TotalSize   = (Format-Bytes -Bytes ([long]$extTotals[$_]))
      FileCount   = [long]$extCounts[$_]
    }
  } |
  Sort-Object -Property TotalBytes -Descending |
  Select-Object -First $TopExtensions

$topDirsResult | Export-Csv -Path $dirCsvPath -NoTypeInformation -Encoding UTF8
$topExtResult | Export-Csv -Path $extCsvPath -NoTypeInformation -Encoding UTF8
if ($driveSummary.Count -gt 0) { $driveSummary | Export-Csv -Path $driveCsvPath -NoTypeInformation -Encoding UTF8 }

$totalLargeFound = $allLargeFiles.Count
$totalTopBytes = 0L
foreach ($x in $top) { $totalTopBytes += [long]$x.LengthBytes }

$runEnded = Get-Date
$duration = $runEnded - $runStarted

function Format-DriveLine {
  param([Parameter(Mandatory = $true)] $d)
  $used = Format-Bytes -Bytes ([long]$d.UsedBytes)
  $free = Format-Bytes -Bytes ([long]$d.FreeBytes)
  $tot = Format-Bytes -Bytes ([long]$d.TotalBytes)
  return ("  {0}  Used: {1} ({2}%)  Free: {3}  Total: {4}" -f $d.Drive, $used, $d.UsedPct, $free, $tot)
}

$summaryLines = New-Object System.Collections.Generic.List[string]
$summaryLines.Add("Disk audit finished: $runEnded") | Out-Null
$summaryLines.Add("Duration: $($duration.ToString())") | Out-Null
$summaryLines.Add("AllLocalDrives: $AllLocalDrives") | Out-Null
$summaryLines.Add("Roots: $($Roots -join '; ')") | Out-Null
$summaryLines.Add("Processed files (total): $processed") | Out-Null
$summaryLines.Add("Large files threshold: $MinFileSizeMB MB") | Out-Null
$summaryLines.Add("Summary threshold: $SummaryMinFileSizeMB MB") | Out-Null
$summaryLines.Add("Large found (>= large threshold): $totalLargeFound file(s)") | Out-Null
$summaryLines.Add("Top exported: $($top.Count) file(s)") | Out-Null
$summaryLines.Add("Top total size: $(Format-Bytes -Bytes $totalTopBytes)") | Out-Null
$summaryLines.Add("Errors (non-fatal): $errors") | Out-Null
$summaryLines.Add("") | Out-Null

if ($driveSummary.Count -gt 0) {
  $summaryLines.Add("Drive summary:") | Out-Null
  foreach ($d in ($driveSummary | Sort-Object Drive)) {
    $summaryLines.Add((Format-DriveLine -d $d)) | Out-Null
  }
  $summaryLines.Add("") | Out-Null
}

$summaryLines.Add("Top directories (bucket depth = $DirDepth, >= $SummaryMinFileSizeMB MB files only):") | Out-Null
foreach ($d in $topDirsResult) {
  $summaryLines.Add(("  {0}  {1}  files: {2}" -f $d.TotalSize, $d.Bucket, $d.FileCount)) | Out-Null
}
$summaryLines.Add("") | Out-Null

$summaryLines.Add("Top extensions (>= $SummaryMinFileSizeMB MB files only):") | Out-Null
foreach ($e in $topExtResult) {
  $summaryLines.Add(("  {0}  {1}  files: {2}" -f $e.TotalSize, $e.Extension, $e.FileCount)) | Out-Null
}
$summaryLines.Add("") | Out-Null

$summaryLines.Add("Outputs:") | Out-Null
$summaryLines.Add("  SUMMARY: $txtPath") | Out-Null
$summaryLines.Add("  TOP FILES CSV: $csvPath") | Out-Null
$summaryLines.Add("  TOP FILES JSON: $jsonPath") | Out-Null
$summaryLines.Add("  TOP DIRS CSV: $dirCsvPath") | Out-Null
$summaryLines.Add("  EXT CSV: $extCsvPath") | Out-Null
if ($driveSummary.Count -gt 0) { $summaryLines.Add("  DRIVE CSV: $driveCsvPath") | Out-Null }
$summaryLines.Add("  LOG: $logPath") | Out-Null

@(
  "Disk audit finished: $runEnded"
  "Duration: $($duration.ToString())"
  "Roots: $($Roots -join '; ')"
  "Processed: $processed file(s)"
  "Large threshold: $MinFileSizeMB MB"
  "Summary threshold: $SummaryMinFileSizeMB MB"
) | Out-File -FilePath $logPath -Encoding UTF8 -Append

$summaryLines | Out-File -FilePath $txtPath -Encoding UTF8

Get-Content -LiteralPath $txtPath

