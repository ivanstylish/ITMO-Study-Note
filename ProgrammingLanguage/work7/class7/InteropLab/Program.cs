using System;
using System.Runtime.InteropServices;
using System.Diagnostics;

namespace InteropLab
{
    class NativeWrapper
    {
        const string LibName = "native_math";

        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern long fib_c_recursive(int n);

        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern long fib_c_iterative(int n);
    }

    class Program
    {
        static long FibManaged(int n)
        {
            if (n <= 1) return n;
            return FibManaged(n - 1) + FibManaged(n - 2);
        }

        static void Main(string[] args)
        {
            int n = 42;
            Console.WriteLine($"[Анализ производительности] Вычисление Fib({n})");

            // 1. Managed C#
            var sw = Stopwatch.StartNew();
            long resCs = FibManaged(n);
            sw.Stop();
            Console.WriteLine($"C# Managed: {resCs} | Время: {sw.ElapsedMilliseconds} мс");

            // 2. Unmanaged C (Recursive)
            sw.Restart();
            long resC = NativeWrapper.fib_c_recursive(n);
            sw.Stop();
            Console.WriteLine($"C Native:   {resC} | Время: {sw.ElapsedMilliseconds} мс");
        }
    }
}
