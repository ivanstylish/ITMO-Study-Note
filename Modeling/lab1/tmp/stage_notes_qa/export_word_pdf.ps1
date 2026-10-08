param([string]$InputDoc, [string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $doc = $word.Documents.Open($InputDoc, $false, $true, $false)
    $doc.Repaginate()
    $doc.ExportAsFixedFormat($OutputPdf, 17)
    Write-Output $OutputPdf
} finally {
    if ($null -ne $doc) {
        $doc.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)
    }
    if ($null -ne $word) {
        $word.Quit(0)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}
