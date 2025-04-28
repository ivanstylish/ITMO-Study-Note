package commands.Handlers;


import command.CommandParser;
import command.CommandRequest;
import command.CommandResponse;
import commands.CommandProcessor;
import model.User;
import state.SessionState;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class ExecuteScriptHandler extends BaseCommandHandler {
    private final CommandProcessor commandProcessor;

    public ExecuteScriptHandler(CommandProcessor cp) {
        this.commandProcessor = cp;
    }

    @Override
    public CommandResponse handle(CommandRequest request, User user) {
        Path scriptPath = null;
        try {
            String filePath = request.getStringArgument("file");
            scriptPath = Paths.get(filePath).toAbsolutePath().normalize();

            // 检查文件是否存在
            if (!Files.exists(scriptPath)) {
                return CommandResponse.error("The script file does not exist:" + scriptPath);
            }

            // 防止递归执行
            if (SessionState.isScriptRunning(scriptPath)) {
                return CommandResponse.error("Recursive script execution detected");
            }
            SessionState.markScriptRunning(scriptPath, true);

            List<String> commands = Files.readAllLines(scriptPath);
            StringBuilder result = new StringBuilder();

            for (String cmdLine : commands) {
                CommandRequest cmdReq = CommandParser.parse(cmdLine);
                CommandResponse response = commandProcessor.process(cmdReq, user);
                result.append(response.getMessage()).append("\n");
            }

            return CommandResponse.success("The script was executed successfully:\n" + result);
        } catch (IOException e) {
            return CommandResponse.error("Failed to read the script:" + e.getMessage());
        } finally {
            SessionState.markScriptRunning(scriptPath, false);
        }
    }
}