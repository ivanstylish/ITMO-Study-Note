package util;

import exception.InvalidInputException;
import manager.CollectionManager;
import model.*;

import java.util.Arrays;

public class InputHandler {
    private final Console console;
    private final CollectionManager manager;

    public InputHandler(CollectionManager manager, Console console) {
        this.console = console;
        this.manager = manager;
    }

    public Product inputProduct() throws InvalidInputException {
        Product product = new Product();

        // 输入名称
        String name = inputNonEmptyString("Product name");
        product.setName(name); // 直接传递非空值

        // 输入坐标
        product.setCoordinates(inputCoordinates());

        // 输入价格
        product.setPrice(inputPositiveLong("Price"));

        // 输入单位
        product.setUnitOfMeasure(inputUnitOfMeasure());

        // 输入制造商
        product.setManufacturer(inputOrganization());

        return product;
    }

    private String inputNonEmptyString(String prompt) {
        while (true) { // 循环直到输入有效
            String input = console.readLine(prompt + ": ").trim();
            if (!input.isEmpty())  {
                return input;
            }
            console.printError("Input cannot be empty！");

            while (console.scanner.hasNextLine()) {
                console.scanner.nextLine();
            }
        }
    }

    private Coordinates inputCoordinates() throws InvalidInputException {
        console.printInfo("\n--- Input coordinate information ---");
        double x = inputDouble("X coordinate (must be > -401)", -401.0);
        float y = inputFloat("Y coordinate (must be <= 569)",569.0f);
        return new Coordinates(x, y);
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

    private UnitOfMeasure inputUnitOfMeasure() {
        console.printInfo("Unit options: " + Arrays.toString(UnitOfMeasure.values()));
        String input = console.readLine("Unit (optional): ");
        return input.isEmpty() ? null : UnitOfMeasure.valueOf(input.toUpperCase());
    }

    private OrganizationType inputOrganizationType() throws InvalidInputException {
        console.printInfo("Available types: " + Arrays.toString(OrganizationType.values()));
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
                System.out.print("Please enter" + prompt + "(must be > 0): ");
                long value = Long.parseLong(console.readLine(prompt + ": "));
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
