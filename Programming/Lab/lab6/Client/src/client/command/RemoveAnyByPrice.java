package client.command;

public class RemoveAnyByPrice implements BaseCommand {
    private long price;
    public RemoveAnyByPrice(long price) {
        this.price = price;
    }

    public long getPrice() {
        return price;
    }

    @Override
    public String getName() {
        return "remove_any_by_price";
    }

    @Override
    public String getDescription() {
        return "удалить из коллекции один элемент, значение поля price которого эквивалентно заданному";
    }
}
