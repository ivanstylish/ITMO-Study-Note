package commandUtil;

import java.util.Scanner;

public interface Command {
    CommandResponse execute(CommandRequest request);
}
