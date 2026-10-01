param([string]$InputDoc, [string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($InputDoc, $false, $true)
    $doc.ExportAsFixedFormat($OutputPdf, 17)
    $doc.Close(0)
    Write-Output $OutputPdf
} finally {
    $word.Quit()
}
