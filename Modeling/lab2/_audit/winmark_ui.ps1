param([string]$Action = 'inspect', [int]$Command = 0, [long]$Window = 0, [int]$Control = 0, [string]$Value = '', [switch]$Quiet)
$ErrorActionPreference = 'Stop'
Add-Type @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public class MarkWindow {
 public delegate bool EnumProc(IntPtr hwnd, IntPtr p);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr hwnd, EnumProc cb, IntPtr p);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int cap);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr hwnd, StringBuilder text, int cap);
 [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr hwnd, int id);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int command);
 [DllImport("user32.dll")] public static extern IntPtr GetMenu(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern int GetMenuItemCount(IntPtr menu);
 [DllImport("user32.dll")] public static extern uint GetMenuItemID(IntPtr menu, int pos);
 [DllImport("user32.dll")] public static extern IntPtr GetSubMenu(IntPtr menu, int pos);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetMenuString(IntPtr menu, uint id, StringBuilder text, int cap, uint flags);
 [DllImport("user32.dll", SetLastError=true)] public static extern bool PostMessage(IntPtr hwnd, uint msg, IntPtr wp, IntPtr lp);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr hwnd, uint msg, IntPtr wp, string text);
 [DllImport("user32.dll")] public static extern bool IsWindowEnabled(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern bool EnableWindow(IntPtr hwnd, bool enabled);
 [DllImport("user32.dll", SetLastError=true)] public static extern IntPtr SendMessageTimeout(IntPtr hwnd, uint msg, IntPtr wp, IntPtr lp, uint flags, uint timeout, out IntPtr result);
 public static uint Target;
 public static List<long> Handles = new List<long>();
 public static bool Collect(IntPtr h, IntPtr p) { uint pid; GetWindowThreadProcessId(h, out pid); if (pid == Target) Handles.Add(h.ToInt64()); return true; }
 public static string Describe(IntPtr h) { var t=new StringBuilder(512); var c=new StringBuilder(256); GetWindowText(h,t,t.Capacity); GetClassName(h,c,c.Capacity); return h.ToInt64()+" id="+GetDlgCtrlID(h)+" class="+c+" enabled="+IsWindowEnabled(h)+" text="+t; }
 public static bool PrintChild(IntPtr h, IntPtr p) { Console.WriteLine("  "+Describe(h)); return true; }
 public static void Menu(IntPtr m, string prefix) { for(int i=0; i<GetMenuItemCount(m); i++){ var t=new StringBuilder(512); GetMenuString(m,(uint)i,t,t.Capacity,0x400); Console.WriteLine(prefix+i+" ID="+GetMenuItemID(m,i)+" "+t); var s=GetSubMenu(m,i); if(s!=IntPtr.Zero) Menu(s,prefix+"  "); } }
}
'@
$proc = Get-Process -Name WinMark -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq 'D:\Study-Note\Modeling\lab2\_audit\winmark\WinMark\WinMark.exe' } | Select-Object -First 1
if (-not $proc) {
    if ($Action -ne 'start') { throw 'WinMark is not running.' }
    $proc = Start-Process -FilePath 'D:\Study-Note\Modeling\lab2\_audit\winmark\WinMark\WinMark.exe' -WorkingDirectory 'D:\Study-Note\Modeling\lab2\_audit\winmark\WinMark' -WindowStyle Hidden -PassThru
    Start-Sleep -Milliseconds 800
}
[MarkWindow]::Target = $proc.Id
[MarkWindow]::EnumWindows([MarkWindow+EnumProc][MarkWindow]::Collect, [IntPtr]::Zero) | Out-Null
if ($Action -eq 'command') {
    if (-not $Window) { $Window = $proc.MainWindowHandle.ToInt64() }
    if (-not [MarkWindow]::PostMessage([IntPtr]$Window, 0x111, [IntPtr]$Command, [IntPtr]::Zero)) { throw "PostMessage failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())" }
    Start-Sleep -Milliseconds 250
} elseif ($Action -eq 'set') {
    $target = [MarkWindow]::GetDlgItem([IntPtr]$Window, $Control)
    [MarkWindow]::SendMessage($target, 0xC, [IntPtr]::Zero, $Value) | Out-Null
}
[MarkWindow]::Handles.Clear()
[MarkWindow]::EnumWindows([MarkWindow+EnumProc][MarkWindow]::Collect, [IntPtr]::Zero) | Out-Null
if (-not $Quiet) { Write-Output "Process $($proc.Id)" }
foreach ($handle in [MarkWindow]::Handles) {
    $h = [IntPtr]$handle
    [MarkWindow]::ShowWindow($h,0) | Out-Null
    if ($Quiet) { continue }
    [MarkWindow]::Describe($h)
    [MarkWindow]::EnumChildWindows($h, [MarkWindow+EnumProc][MarkWindow]::PrintChild, [IntPtr]::Zero) | Out-Null
    $menu = [MarkWindow]::GetMenu($h)
    if ($menu -ne [IntPtr]::Zero) { [MarkWindow]::Menu($menu,'  ') }
}




