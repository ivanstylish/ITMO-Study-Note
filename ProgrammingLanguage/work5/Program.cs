using System;
using System.Diagnostics;
using System.Threading.Tasks;

namespace class5
{
    public class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("Async Data Aggregation - Performance Comparison\n");

            IExternalDataService externalService = new SlowExternalDataService();
            IPageAggregator aggregator = new PageAggregatorService(externalService);

            int userId = 12345;
            Stopwatch stopwatch = new Stopwatch();

            // Test 1: Sequential Strategy
            stopwatch.Start();
            var sequentialResult = await aggregator.LoadPageDataSequentialAsync(userId);
            stopwatch.Stop();

            Console.WriteLine("\n" + sequentialResult);
            Console.WriteLine($"Sequential Time: {stopwatch.ElapsedMilliseconds} ms\n");

            stopwatch.Reset();
            await Task.Delay(500);

            // Test 2: Parallel Strategy
            stopwatch.Start();
            var parallelResult = await aggregator.LoadPageDataParallelAsync(userId);
            stopwatch.Stop();

            Console.WriteLine("\n" + parallelResult);
            Console.WriteLine($"Parallel Time: {stopwatch.ElapsedMilliseconds} ms\n");
        }
    }
}