public class Calculator {

    public int add(int a, int b) {
        return a + b; // Simplified and dead code removed
    }

    public int subtract(int a, int b) {
        return a - b; // Simplified
    }

    public static void main(String[] args) {
        Calculator calc = new Calculator();
        int sum = calc.add(5, 3);
        System.out.println("Sum: " + sum);

        int difference = calc.subtract(10, 4); // Now the result is used
        System.out.println("Difference: " + difference);
    }
}