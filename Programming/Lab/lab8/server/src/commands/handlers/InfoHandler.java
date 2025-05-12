package commands.handlers;

import commandUtil.CommandRequest;
import commandUtil.CommandResponse;
import model.Product;
import user.User;

import java.util.Date;
import java.util.concurrent.ConcurrentHashMap;

public class InfoHandler extends BaseCommandHandler {
    private final ConcurrentHashMap<Long, Product> collection;
    private final Date initDate = new Date();

    public InfoHandler(ConcurrentHashMap<Long, Product> collection) {
        this.collection = collection;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        String info = String.format("""
            Type: %s
            InitTime: %s
            quantity of elements: %d
            """, collection.getClass().getSimpleName(), initDate, collection.size());
        return CommandResponse.success(info);
    }
}
