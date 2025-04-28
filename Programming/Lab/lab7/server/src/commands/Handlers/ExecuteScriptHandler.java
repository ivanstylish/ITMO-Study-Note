package commands.Handlers;


import command.CommandParser;
import commands.CommandProcessor;
import command.CommandRequest;
import command.CommandResponse;
import model.User;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static java.nio.file.Files.readString;

public class ExecuteScriptHandler extends BaseCommandHandler {
    private final CommandProcessor commandProcessor;

    public ExecuteScriptHandler(CommandProcessor cp) {
        this.commandProcessor = cp;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        try {
            String filePath = request.getStringArgument("file");
            List<String> commands = Files.readAllLines(Path.of(filePath));

            StringBuilder result = new StringBuilder();
            for (String cmdLine : commands) {
                CommandRequest cmdRe = CommandParser.parse(cmdLine);
                CommandResponse response = commandProcessor.process(cmdRe, user);
                result.append(response.getMessage()).append("\n");
            }
            return CommandResponse.success("Script executed successfully:\n" + result);
        }
        catch (IOException e) {
            return CommandResponse.error("Script read failed: " , e.getMessage());
        }
    }
}