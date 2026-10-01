param([string]$Action='load',[string]$File='',[int]$Command=0,[string]$Output='')
$ErrorActionPreference='Stop'
$batchAction=$Action; $batchCommand=$Command
. "$PSScriptRoot\winmark_ui.ps1" -Quiet
$Action=$batchAction; $Command=$batchCommand
function Handles {
 [MarkWindow]::Handles.Clear()
 [MarkWindow]::EnumWindows([MarkWindow+EnumProc][MarkWindow]::Collect,[IntPtr]::Zero)|Out-Null
 return [MarkWindow]::Handles.ToArray()
}
function Find-Class([string]$Class) {
 foreach($h in (Handles)) {
  $c=New-Object Text.StringBuilder 256
  [MarkWindow]::GetClassName([IntPtr]$h,$c,256)|Out-Null
  if($c.ToString() -eq $Class){return $h}
 }
 throw "Window class not found: $Class"
}
function Find-Control([int]$Id) {
 for($attempt=0; $attempt -lt 10; $attempt++) {
  foreach($h in (Handles)) { if([MarkWindow]::GetDlgItem([IntPtr]$h,$Id) -ne [IntPtr]::Zero){return $h} }
  Start-Sleep -Milliseconds 200
 }
 throw "Control not found: $Id"
}
function Command-To([long]$Handle,[int]$Id) {
 [MarkWindow]::ShowWindow([IntPtr]$Handle,7)|Out-Null
 if(-not [MarkWindow]::PostMessage([IntPtr]$Handle,0x111,[IntPtr]$Id,[IntPtr]::Zero)){throw 'Command failed'}
 Start-Sleep -Milliseconds 350
}
function Set-Edit([long]$Handle,[int]$Id,[string]$Text) {
 [MarkWindow]::SendMessage([MarkWindow]::GetDlgItem([IntPtr]$Handle,$Id),0xC,[IntPtr]::Zero,$Text)|Out-Null
}
function Export-Report([long]$Main,[string]$Path) {
 Command-To $Main 32801
 $dialog=Find-Control 1033
 foreach($id in @(1033,1034,1035,1036,1037)) {
  $ctrl=[MarkWindow]::GetDlgItem([IntPtr]$dialog,$id)
  if([MarkWindow]::IsWindowEnabled($ctrl)){[MarkWindow]::SendMessage($ctrl,0xF1,[IntPtr]1,$null)|Out-Null}
 }
 foreach($id in @(1038,1039)){[MarkWindow]::SendMessage([MarkWindow]::GetDlgItem([IntPtr]$dialog,$id),0xF1,[IntPtr]0,$null)|Out-Null}
 Command-To $dialog 1
 $save=Find-Control 1152
 Set-Edit $save 1152 $Path
 Command-To $save 1
 $message=Find-Control 20
 Command-To $message 2
}
$main=Find-Class 'Afx:400000:0'
if($Action -eq 'load' -or $Action -eq 'open') {
 Command-To $main 32771
 $dialog=Find-Control 1152
 Set-Edit $dialog 1152 $File
 Command-To $dialog 1
 if($Action -eq 'load') {
  Command-To $main 32786
  $matrix=Find-Class 'AfxFrameOrView42'
  Command-To $matrix 32787
 }
} elseif($Action -eq 'main') { Command-To $main $Command }
elseif($Action -eq 'savefile') {
 $dialog=Find-Control 1152
 Set-Edit $dialog 1152 $File
 Command-To $dialog 1
}
elseif($Action -eq 'export') {
 try { $pi=Find-Control 1014; Command-To $pi 1 } catch {}
 Command-To $main 32801
 $dialog=Find-Control 1033
 foreach($id in @(1033,1034,1035,1036,1037)) {
  $ctrl=[MarkWindow]::GetDlgItem([IntPtr]$dialog,$id)
  if([MarkWindow]::IsWindowEnabled($ctrl)){[MarkWindow]::SendMessage($ctrl,0xF1,[IntPtr]1,$null)|Out-Null}
 }
 foreach($id in @(1038,1039)){[MarkWindow]::SendMessage([MarkWindow]::GetDlgItem([IntPtr]$dialog,$id),0xF1,[IntPtr]0,$null)|Out-Null}
 Command-To $dialog 1
 $save=Find-Control 1152
 Set-Edit $save 1152 $File
 Command-To $save 1
 try { $message=Find-Control 20; Command-To $message 2 } catch {}
}
elseif($Action -eq 'run') {
 Command-To $main 32771
 $dialog=Find-Control 1152
 Set-Edit $dialog 1152 $File
 Command-To $dialog 1
 Command-To $main 32780
 $pi=Find-Control 1014
 Command-To $pi 1
 Command-To $main 32779
 $frame=Find-Class 'AfxFrameOrView42'
 $editor=[MarkWindow]::GetDlgItem([IntPtr]$frame,142).ToInt64()
 Command-To $editor 1005
 Command-To $main 32781
 $metrics=Find-Control 1015
 Command-To $metrics 1
 Export-Report $main $Output
 Command-To $main 32772
 $save=Find-Control 1152
 Set-Edit $save 1152 ($Output -replace '\.html$','_executed.mrk')
 Command-To $save 1
 Write-Output "Calculated and exported: $Output"
}
foreach($h in (Handles)) {
 [MarkWindow]::ShowWindow([IntPtr]$h,0)|Out-Null
 if ($Action -eq 'run') { continue }
 [MarkWindow]::Describe([IntPtr]$h)
 [MarkWindow]::EnumChildWindows([IntPtr]$h,[MarkWindow+EnumProc][MarkWindow]::PrintChild,[IntPtr]::Zero)|Out-Null
}






