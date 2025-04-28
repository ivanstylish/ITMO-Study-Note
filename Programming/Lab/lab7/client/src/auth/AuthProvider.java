package auth;

import command.CommandRequest;
import command.CommandResponse;
import command.CommandType;
import dao.UserDAO;
import exception.NetworkConException;
import exception.NetworkException;
import model.User;
import network.ServerProxy;

import java.sql.SQLException;

public class AuthProvider {
    private final ServerProxy proxy;
    private final UserDAO userDAO;
    private User currentUser;


    public AuthProvider(ServerProxy proxy, UserDAO userDAO) {
        this.proxy = proxy;
        this.userDAO = userDAO;
    }

    public CommandResponse login(String username, String password) throws NetworkException, NetworkConException {
        // 发送认证请求到服务端
        CommandRequest request = new CommandRequest()
                .setCommandType(CommandType.AUTH)
                .addArgument("username", username)
                .addArgument("password", password);

        CommandResponse response = proxy.sendRequest(request);
        if (response.isSuccess()) {
            currentUser = (User) response.getData();
            return response;
        } else {
            return CommandResponse.error(response.getMessage(), null);
        }
    }


    public User getCurrentUser() {
        return currentUser;
    }
}
