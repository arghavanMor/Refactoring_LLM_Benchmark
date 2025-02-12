public class StringProcessor {

    public String reverseString(String str) {
        String reversed = "";
        for (int i = str.length() - 1; i >= 0; i--) {
            reversed += str.charAt(i);
        }
        return reversed;
    }

    public static void main(String args) {
        StringProcessor processor = new StringProcessor();
        String reversed = processor.reverseString("hello");
        System.out.println(reversed);
    }
}