using System;

public class SlowExternalDataService : IExternalDataService
{
	public async Task<string> GetUserDataAsync(int userId)
	{
        Console.WriteLine($"GetUserDataAsync for userId: {userId}");
		await Task.Delay( 2000 );
        Console.WriteLine($"Got UserData for userId: {userId}");


        return $"User #{userId}: John Wick, email: john@example.com";
    }

	public async Task<string> GetUserOrdersAsync(int userId)
	{
        Console.WriteLine($"GetUserOrdersAsync for userId: {userId}");
		await Task.Delay(3000);
        Console.WriteLine($"Got UserOrders for userId: {userId}");

		return $"Orders for User #{userId}: order#1, order#2";

    }

    public async Task<string> GetAdsAsync()
    {
        Console.WriteLine("GetAdsAsync");
        await Task.Delay(1000); 
        Console.WriteLine("GotAdsAsync");

        return "Ads: Special offer - 50% discount on electronics!";
    }
}
