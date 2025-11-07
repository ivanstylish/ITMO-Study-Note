using System;

public class PageAggregatorService : IPageAggregator
{
    private readonly IExternalDataService _externalDataService;


    public PageAggregatorService(IExternalDataService externalDataService)
    {
        _externalDataService = externalDataService;
    }

    public async Task<PagePayload> LoadPageDataSequentialAsync(int userId)
    {
        Console.WriteLine("\n=======================");
        Console.WriteLine("SEQUENTIAL STRATEGY");
        Console.WriteLine("\n=======================");


        var UserData = await _externalDataService.GetUserDataAsync(userId);
        var OrderData = await _externalDataService.GetUserOrdersAsync(userId);
        var AdData = await _externalDataService.GetAdsAsync();

        return new PagePayload
        {
            UserData = UserData,
            OrderData = OrderData,
            AdData = AdData
        };
    }

public async Task<PagePayload> LoadPageDataParallelAsync(int userId)
{
    Console.WriteLine("\n========================================");
    Console.WriteLine("PARALLEL STRATEGY");
    Console.WriteLine("========================================\n");

    var userDataTask = _externalDataService.GetUserDataAsync(userId);
    var orderDataTask = _externalDataService.GetUserOrdersAsync(userId);
    var adDataTask = _externalDataService.GetAdsAsync();

    await Task.WhenAll(userDataTask, orderDataTask, adDataTask);

    return new PagePayload
    {
        UserData = userDataTask.Result,
        OrderData = orderDataTask.Result,
        AdData = adDataTask.Result
    };
}
}
