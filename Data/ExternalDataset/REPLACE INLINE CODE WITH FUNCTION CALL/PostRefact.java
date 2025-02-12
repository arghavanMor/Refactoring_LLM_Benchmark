public class OrderProcessor {

    private double calculateDiscount(int quantity, double basePrice) { // Extracted function
        if (quantity > 10) {
            return basePrice * 0.10;
        }
        return 0;
    }

    public double calculateTotal(int quantity, double pricePerUnit) {
        double basePrice = quantity * pricePerUnit;
        double discount = calculateDiscount(quantity, basePrice); // Call the function
        return basePrice - discount;
    }

    public void processOrder(int quantity, double pricePerUnit) {
        double basePrice = quantity * pricePerUnit;
        double discount = calculateDiscount(quantity, basePrice); // Call the function
        double total = basePrice - discount;

        System.out.println("Order Total: " + total);
        // ... other order processing logic
    }

    public static void main(String[] args) {
        OrderProcessor processor = new OrderProcessor();
        double orderTotal = processor.calculateTotal(15, 20.0);
        System.out.println("Calculated Total: " + orderTotal);

        processor.processOrder(5, 10.0);
    }
}