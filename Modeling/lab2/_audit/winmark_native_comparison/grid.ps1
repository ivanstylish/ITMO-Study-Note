param([long]$Grid,[int]$X,[int]$Y,[string]$Text)
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class GridInput {
 [StructLayout(LayoutKind.Sequential)] public struct Rect {public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out Rect r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h,uint flags);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint flags,uint x,uint y,uint data,UIntPtr info);
}
'@
$rect=New-Object GridInput+Rect
[GridInput]::GetWindowRect([IntPtr]$Grid,[ref]$rect)|Out-Null
[GridInput]::SetForegroundWindow([GridInput]::GetAncestor([IntPtr]$Grid,2))|Out-Null
[GridInput]::SetCursorPos(($rect.Left+$X),($rect.Top+$Y))|Out-Null
Start-Sleep -Milliseconds 150
foreach($i in 1..2){[GridInput]::mouse_event(2,0,0,0,[UIntPtr]::Zero);[GridInput]::mouse_event(4,0,0,0,[UIntPtr]::Zero);Start-Sleep -Milliseconds 80}
$shell=New-Object -ComObject WScript.Shell
if($Text){$shell.SendKeys('^a');$shell.SendKeys($Text);$shell.SendKeys('{ENTER}')}
Start-Sleep -Milliseconds 150
Write-Output "Edited grid cell at $X,$Y"
