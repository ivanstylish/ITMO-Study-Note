package util;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

public class HashUtil {
    private static final String HASH_ALGORITHM = "SHA-384";


    // 验证密码
    public static boolean validate(String inputPassword, String storedHash) {
        try {
            MessageDigest md = MessageDigest.getInstance(HASH_ALGORITHM);
            byte[] decodedHash = Base64.getDecoder().decode(storedHash);
            byte[] inputHash = md.digest(inputPassword.getBytes());
            return MessageDigest.isEqual(decodedHash, inputHash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}