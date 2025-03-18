package client.parsers;

import client.command.BaseCommand;
import client.exception.InvalidCommandException;
import exception.EmptyInputException;
import exception.InvalidInputException;
import exception.WrongLengthException;

import java.util.Map;

public interface CommandFactory {
    BaseCommand create(Map<String, String> params) throws InvalidCommandException, InvalidInputException, EmptyInputException, WrongLengthException;
}
