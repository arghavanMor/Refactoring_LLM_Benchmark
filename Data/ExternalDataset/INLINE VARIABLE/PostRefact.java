public class CalculateTotalPrice {

    public double calculate(int quantity, double pricePerUnit) {
        return (quantity * pricePerUnit) * 1.10; // Inlined the variable
    }

    public static void main(String[] args) {
        CalculateTotalPrice calculator = new CalculateTotalPrice();
        double totalPrice = calculator.calculate(5, 10.0);
        System.out.println("Total Price: " + totalPrice);
    }
}