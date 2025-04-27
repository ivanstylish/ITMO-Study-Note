package auth;

import command.CommandRequest;
import command.CommandResponse;
import command.CommandType;
import exception.NetworkException;
import model.User;
import network.ServerProxy;

public class AuthProvider {
    private final ServerProxy proxy;
    private User currentUser;

    public AuthProvider(ServerProxy proxy) {
        this.proxy = proxy;
    }

    public boolean login(String username, String password) throws NetworkException {
        // 发送认证请求到服务端
        CommandRequest request = new CommandRequest();
        request.setCommandType(CommandType.AUTH);
        request.setUsername(username);
        request.setPassword(password);

        CommandResponse response = proxy.sendRequest(request);
        if (response.isSuccess()) {
            this.currentUser = (User) response.getData();
            return true;
        }
        return false;
    }

    public User getCurrentUser() {
        return currentUser;
    }
}
