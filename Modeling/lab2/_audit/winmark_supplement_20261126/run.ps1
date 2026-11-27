param([ValidateSet('system1','system2','comparison')][string]$Model)
$ErrorActionPreference='Stop'
$root=(Resolve-Path -LiteralPath "$PSScriptRoot\..\..").Path
$dest="$root\Calculation_data\WinMark\ReportSupplement"
$inputPath="$PSScriptRoot\${Model}_input.mrk"
$native=Get-Process WinMark -ErrorAction SilentlyContinue | Where-Object Path -eq "$root\WinMark\WinMark.exe" | Select-Object -First 1
if(!$native){$native=Start-Process -FilePath "$root\WinMark\WinMark.exe" -WorkingDirectory $PSScriptRoot -PassThru}
Start-Sleep -Milliseconds 450
. "$PSScriptRoot\..\winmark_native_comparison\ui.ps1" -Quiet
[MarkWindow]::Target=$native.Id
function Windows {
 [MarkWindow]::Handles.Clear()
 [MarkWindow]::EnumWindows([MarkWindow+EnumProc][MarkWindow]::Collect,[IntPtr]::Zero)|Out-Null
 [MarkWindow]::Handles.ToArray()
}
function Find([string]$Class='', [int]$Control=0, [string]$Title='') {
 for($attempt=0;$attempt -lt 20;$attempt++){
  foreach($win in (Windows)){
   $desc=[MarkWindow]::Describe([IntPtr]$win)
   if($Class -and $desc -notmatch "class=$Class"){continue}
   if($Title -and $desc -notlike "*$Title*"){continue}
   if($Control -and [MarkWindow]::GetDlgItem([IntPtr]$win,$Control) -eq [IntPtr]::Zero){continue}
   return [IntPtr]$win
  }
  Start-Sleep -Milliseconds 120
 }
 $current=(Windows | ForEach-Object {[MarkWindow]::Describe([IntPtr]$_)}) -join ', '
 throw "Missing WinMark window: $Class / $Control / $Title. Current windows: $current"
}
function Press([IntPtr]$Window,[int]$Id){
 if(-not [MarkWindow]::PostMessage($Window,0x111,[IntPtr]$Id,[IntPtr]::Zero)){throw "WinMark command $Id failed"}
 Start-Sleep -Milliseconds 160
}
function SetText([IntPtr]$Window,[int]$Id,[string]$Value){
 [MarkWindow]::SendMessage([MarkWindow]::GetDlgItem($Window,$Id),0xC,[IntPtr]::Zero,$Value)|Out-Null
}
function FileDialog([string]$Path){$dlg=Find -Control 1152;Start-Sleep -Milliseconds 550;SetText $dlg 1152 $Path;Start-Sleep -Milliseconds 100;Press $dlg 1}
function SelectItem([IntPtr]$Window,[int]$Id,[int]$Index){
 [MarkWindow]::SendMessage([MarkWindow]::GetDlgItem($Window,$Id),0x14E,[IntPtr]$Index,$null)|Out-Null
}
function Curve([IntPtr]$Graph,[string]$Name,[int]$Color){
 Press $Graph 32791
 $dlg=Find -Control 1016 -Title 'Добавить график'
 $index=[MarkWindow]::SendMessage([MarkWindow]::GetDlgItem($dlg,1016),0x158,[IntPtr](-1),$Name).ToInt32()
 if($index -lt 0){throw "Missing curve: $Name"}
 SelectItem $dlg 1016 $index
 SelectItem $dlg 1018 $Color
 SelectItem $dlg 1021 $Color
 SelectItem $dlg 1020 1
 SelectItem $dlg 1019 $Color
 SelectItem $dlg 1022 3
 Press $dlg 1
}
try {
 $main=Find -Class 'Afx:400000:0'
 Press $main 32771
 FileDialog $inputPath
 Press $main 32780
 Press (Find -Control 1014) 1
 Press $main 32781
 Press (Find -Control 1015) 1
 Press $main 32777
 $settings=Find -Class 'AfxFrameOrView42' -Control 101
 Press ([MarkWindow]::GetDlgItem($settings,142)) 1005
 Press $main 32782
 $scan=Find -Class 'AfxFrameOrView42' -Control 101
 Press ([MarkWindow]::GetDlgItem($scan,142)) 1005
 if($Model -eq 'comparison'){
  Press $main 32783
  $graph=Find -Control 162
  Curve $graph Loss1 1
  Curve $graph Loss2 2
  Press $graph 32792
  $axes=Find -Title 'Формат осей'
  foreach($id in 1030,1032){[MarkWindow]::SendMessage([MarkWindow]::GetDlgItem($axes,$id),0xF5,[IntPtr]::Zero,$null)|Out-Null}
  foreach($v in @(@(1007,'0'),@(1024,'0.9'),@(1025,'0.1'),@(1026,'1'),@(1027,'10'),@(1028,'1'))){SetText $axes $v[0] $v[1]}
  foreach($id in 1033,1035){[MarkWindow]::SendMessage([MarkWindow]::GetDlgItem($axes,$id),0xF1,[IntPtr]1,$null)|Out-Null}
  Press $axes 1
  & "$PSScriptRoot\..\winmark_native_comparison\capture.ps1" -Window $graph.ToInt64() -Output "$PSScriptRoot\loss_window.png"
  Press $graph 32800
  $dlg=Find -Control 1152
  SelectItem $dlg 1136 3
  [MarkWindow]::PostMessage($dlg,0x111,[IntPtr](65536+1136),[MarkWindow]::GetDlgItem($dlg,1136))|Out-Null
  SetText $dlg 1152 "$dest\loss_comparison.png"
  Press $dlg 1
  Start-Sleep -Milliseconds 250
 }
 Press $main 32801
 $dialog=Find -Control 1033 -Class '#32770'
 foreach($id in 1033,1034,1035,1036,1037){
  $ctrl=[MarkWindow]::GetDlgItem($dialog,$id)
  if([MarkWindow]::IsWindowEnabled($ctrl)){[MarkWindow]::SendMessage($ctrl,0xF1,[IntPtr]1,$null)|Out-Null}
 }
 foreach($id in 1038,1039){[MarkWindow]::SendMessage([MarkWindow]::GetDlgItem($dialog,$id),0xF1,[IntPtr]0,$null)|Out-Null}
 Press $dialog 1
 FileDialog "$dest\$Model.html"
 Press (Find -Class '#32770' -Control 20) 2
 Press $main 32772
 FileDialog "$dest\$Model.mrk"
 if(!(Test-Path -LiteralPath "$dest\$Model.html") -or !(Test-Path -LiteralPath "$dest\$Model.mrk")){throw 'Native outputs not found'}
 Write-Output "WinMark ran and saved $Model"
} finally {}
