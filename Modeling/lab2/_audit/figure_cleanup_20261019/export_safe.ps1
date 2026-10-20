param([string]$InputDoc,[string]$OutputPdf)
$ErrorActionPreference='Stop'
$word=$null
$document=$null
$ownsInstance=$false
try {
 $word=New-Object -ComObject Word.Application
 # Never quit or change visibility of an existing user editing instance.
 if($word.Documents.Count -ne 0){throw 'The Word instance contains existing documents; export stopped.'}
 $ownsInstance=$true
 $word.Visible=$false
 $word.DisplayAlerts=0
 $document=$word.Documents.Open($InputDoc,$false,$true)
 $document.ExportAsFixedFormat($OutputPdf,17)
 $document.Close(0)
 $document=$null
 Write-Output $OutputPdf
} finally {
 if($document -ne $null){$document.Close(0)}
 if($ownsInstance -and $word -ne $null){$word.Quit()}
}
