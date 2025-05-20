package server.commands;

import common.network.requests.Request;
import common.network.responses.Response;

/**
 * Interface for all executable commands.
 */
public interface Executable {
  Response apply(Request request);
}
