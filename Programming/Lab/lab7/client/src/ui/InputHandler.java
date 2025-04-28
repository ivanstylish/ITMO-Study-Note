package ui;

import exception.EmptyInputException;
import exception.InvalidInputException;
import exception.WrongLengthException;
import model.*;


import java.util.Arrays;


public class InputHandler {
    private final Console console;

    public InputHandler(Console console) {
        this.console = console;
    }

    public Product inputProduct() throws InvalidInputException, WrongLengthException {
        Product product = new Product();
        try {
            console.printInfo("\n--- Enter product information ---");
            product.setName(inputNonEmptyString("Product name"));
            product.setPrice(inputPositiveLong("Price"));
            product.setCoordinates(inputCoordinates());
            product.setManufacturer(inputOrganization());
            product.setUnitOfMeasure(inputUnitOfMeasure());
            return product;
        } catch (EmptyInputException | InvalidInputException e) {
            console.printError("Failed to create product: " + e.getMessage());
            throw new InvalidInputException("Product creation failed");
        }
    }

    private String inputNonEmptyString(String prompt) {
        while (true) { // 循环直到输入有效
            String input = console.readLine(prompt + ": ").trim();
            if (!input.isEmpty())  {
                return input;
            }
            console.printError("Input cannot be empty!");
            console.clearInputBuffer();
        }
    }

    private Coordinates inputCoordinates() throws InvalidInputException {
        console.printInfo("\n--- Input coordinate information ---");
        try {
            double x = inputDouble("X coordinate (must be > -401)", -401.0);
            float y = inputFloat("Y coordinate (must be <= 569)", 569.0f);
            Coordinates coord = new Coordinates(x, y);
            console.printInfo("Created coordinates: " + coord);
            return coord;
        } catch (IllegalArgumentException e) {
            throw new InvalidInputException("Invalid coordinate value: " + e.getMessage());
        }
    }

    private Organization inputOrganization() throws InvalidInputException {
        console.printInfo("\n--- Enter organization information ---");
        Organization org = new Organization();

        org.setName(inputNonEmptyString("Organization name"));
        org.setFullName(inputFullName());
        org.setType(inputOrganizationType());

        return org;
    }

    private String inputFullName() throws InvalidInputException {
        String input = console.readLine("Full name (max 1125): ");
        if (input.length() > 1125) {
            throw new InvalidInputException("Name too long");
        }
        return input;
    }

    public UnitOfMeasure inputUnitOfMeasure() {
        console.printInfo("\nUnit options: " + Arrays.toString(UnitOfMeasure.values()));
        String input = console.readLine("Unit (optional): ");
        return input.isEmpty() ? null : UnitOfMeasure.valueOf(input.toUpperCase());
    }

    private OrganizationType inputOrganizationType() throws InvalidInputException {
        console.printInfo("\nAvailable types: " + Arrays.toString(OrganizationType.values()));
        while (true) {
            try {
                String input = console.readLine("Please select the type of organization: ").trim().toUpperCase();
                return OrganizationType.valueOf(input);
            } catch (IllegalArgumentException e) {
                throw new InvalidInputException("Invalid organization type");
            }
        }
    }

    private long inputPositiveLong(String prompt) throws NumberFormatException {
        while (true) {
            try {
                String input = console.readLine(prompt + " (must be > 0): ");
                long value = Long.parseLong(input);
                if (value > 0) return value;
                console.printError("Must be positive");
            } catch (NumberFormatException e) {
                System.out.println("Invalid entry, please enter a positive integer!");
            }
        }
    }

    private double inputDouble(String prompt, double min) throws InvalidInputException {
        while (true) {
            try {
                double value = Double.parseDouble(console.readLine(prompt + ": "));
                if (value <= min) {
                    throw new InvalidInputException("Wrong range error");
                }
                return value;
            } catch (NumberFormatException e) {
                System.out.println("Please enter a valid number!");
            }
        }
    }

    private float inputFloat(String prompt, float max) throws InvalidInputException {
        while (true) {
            try {
                float value = Float.parseFloat(console.readLine(prompt + ": "));
                if (value > max) {
                    throw new InvalidInputException("Wrong range error");
                }
                return value;
            } catch (NumberFormatException e) {
                System.out.println("Please enter a valid number!");
            }
        }
    }
}
