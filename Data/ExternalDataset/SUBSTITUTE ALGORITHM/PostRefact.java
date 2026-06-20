public class StringProcessor {

    public String reverseString(String str) {
        return new StringBuilder(str).reverse().toString(); // Use StringBuilder
    }

    public static void main(String[] args) {
        StringProcessor processor = new StringProcessor();
        String reversed = processor.reverseString("hello");
        System.out.println(reversed);
    }
}