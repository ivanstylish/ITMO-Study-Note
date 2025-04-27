package util;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

public class HashUtil {
    private static final String HASH_ALGORITHM = "SHA-256";

    // 生成密码哈希
    public static String hash(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance(HASH_ALGORITHM);
            byte[] salt = new byte[16];
            new SecureRandom().nextBytes(salt);
            md.update(salt);
            byte[] hashedPassword = md.digest(password.getBytes());
            return Base64.getEncoder().encodeToString(hashedPassword);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("哈希算法不支持: " + HASH_ALGORITHM, e);
        }
    }

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