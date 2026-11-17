param([long]$Window,[string]$Output)
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class NativeCapture {
 [StructLayout(LayoutKind.Sequential)] public struct Rect {public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out Rect r);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int hgt,bool repaint);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int command);
}
'@
[NativeCapture]::ShowWindow([IntPtr]$Window,9)|Out-Null
[NativeCapture]::SetForegroundWindow([IntPtr]$Window)|Out-Null
Start-Sleep -Milliseconds 150
$rect=New-Object NativeCapture+Rect
[NativeCapture]::GetWindowRect([IntPtr]$Window,[ref]$rect)|Out-Null
$bitmap=New-Object Drawing.Bitmap ($rect.Right-$rect.Left),($rect.Bottom-$rect.Top)
$graphics=[Drawing.Graphics]::FromImage($bitmap)
$dc=$graphics.GetHdc()
[NativeCapture]::PrintWindow([IntPtr]$Window,$dc,0)|Out-Null
$graphics.ReleaseHdc($dc)
$bitmap.Save($Output,[Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose();$bitmap.Dispose()
