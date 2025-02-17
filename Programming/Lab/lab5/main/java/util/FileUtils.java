package util;

import java.util.Scanner;

public class FileUtils {
    public static String readFile(String path) throws Exception {
        try (Scanner scanner = new Scanner(new java.io.File(path))) {
            StringBuilder sb = new StringBuilder();
            while (scanner.hasNextLine()) {
                sb.append(scanner.nextLine());
            }
            return sb.toString();
        }
    }

    public static void writeFile(String path, String content) throws Exception {
        try (java.io.FileWriter writer = new java.io.FileWriter(path)){
            writer.write(content);
        }
    }
}
