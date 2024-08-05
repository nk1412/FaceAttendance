import java.math.*;
import java.util.*;

class ja {
    public static void main(String args[]) {
        int p, q, n, phi, e, d = 0, i;

        // Taking two prime numbers
        p = 7;
        q = 11;

        // Calculating n
        n = p * q;

        // Calculating phi
        phi = (p - 1) * (q - 1);

        // Generating public key
        for (e = 2; e < phi; e++) {
            // e must be less than phi and GCD of (e, phi) must be 1
            if (gcd(e, phi) == 1) {
                break;
            }
        }
        System.out.println("The value of e = " + e);

        // Generating private key
        for (i = 0;; i++) {
            int x = 1 + (i * phi);
            if (x % e == 0) {
                d = x / e;
                break;
            }
        }
        System.out.println("The value of d = " + d);

        // The data to be encrypted and decrypted
        int plain_text = 9;
        System.out.println("The message sent is : " + plain_text);
        double cipher_text;
        BigInteger msg;

        // Encrypting the data
        cipher_text = (Math.pow(plain_text, e)) % n;
        System.out.println("Encrypted message is : " + cipher_text);
        // converting int value of n to BigInteger
        BigInteger N = BigInteger.valueOf(n);

        // converting float value of cipher_text to BigInteger
        BigInteger C = BigDecimal.valueOf(cipher_text).toBigInteger();

        msg = (C.pow(d)).mod(N);
        System.out.println("Decrypted message is : " + msg);
    }

    static int gcd(int e, int phi) {
        if (e == 0)
            return phi;
        else
            return gcd(phi % e, e);
    }
}
