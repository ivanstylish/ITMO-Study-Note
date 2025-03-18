package client.command;

import java.io.Serializable;

public interface BaseCommand extends Serializable {
    String getName();
    String getDescription();
}
