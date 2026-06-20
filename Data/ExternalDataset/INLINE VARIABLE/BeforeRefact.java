public class CalculateTotalPrice {

    public double calculate(int quantity, double pricePerUnit) {
        double basePrice = quantity * pricePerUnit; // The variable to be inlined
        return basePrice * 1.10; // Applying tax
    }

    public static void main(String[] args) {
        CalculateTotalPrice calculator = new CalculateTotalPrice();
        double totalPrice = calculator.calculate(5, 10.0);
        System.out.println("Total Price: " + totalPrice);
    }
}