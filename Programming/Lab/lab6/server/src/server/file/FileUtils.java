package server.file;

import java.nio.file.Files;
import java.nio.file.Paths;


public class FileUtils {
    public static String readFile(String path) throws Exception {
        return new String(Files.readAllBytes(Paths.get(path)));
    }

    public static void writeFile(String path, String content) throws Exception {
        Files.write(Paths.get(path), content.getBytes());
    }
}
