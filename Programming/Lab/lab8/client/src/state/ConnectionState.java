package state;

/**
 * Managing client-server connection status
 */
public class ConnectionState {
    private String serverHost;
    private int serverPort;
    private boolean isConnected;

    public void setServerAddress(String host, int port) {
        this.serverHost = host;
        this.serverPort = port;
    }

    public boolean checkConnection() {
        return isConnected;
    }

    public void setConnected(boolean connected) {
        isConnected = connected;
    }

    public String getServerHost() {
        return serverHost;
    }

    public int getServerPort() {
        return serverPort;
    }
}
