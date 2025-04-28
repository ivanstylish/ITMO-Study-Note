package ui;
public interface Console {
    String readLine(String prompt);
    void printInfo(String message);
    void printError(String message);
    void clearInputBuffer();
}