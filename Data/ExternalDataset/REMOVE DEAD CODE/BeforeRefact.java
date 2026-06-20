public class Calculator {

    public int add(int a, int b) {
        int result = a + b;
        return result;

        int unusedVariable = 10; // Dead code: Never used
        System.out.println("This will never print"); // Dead code: Unreachable
    }

    public int subtract(int a, int b) {
        int result = a - b;
        return result;
    }

    public static void main(String[] args) {
        Calculator calc = new Calculator();
        int sum = calc.add(5, 3);
        System.out.println("Sum: " + sum);

        calc.subtract(10, 4); // Result is calculated but not used. Dead code?
    }
}