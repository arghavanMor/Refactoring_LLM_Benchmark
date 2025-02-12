public class OrderProcessor {

    public double calculateTotal(int quantity, double pricePerUnit) {
        double basePrice = quantity * pricePerUnit;
        double discount = 0;
        if (quantity > 10) {
            discount = basePrice * 0.10; // 10% discount
        }
        return basePrice - discount;
    }

    public void processOrder(int quantity, double pricePerUnit) {
        double basePrice = quantity * pricePerUnit; // Duplicate code
        double discount = 0;
        if (quantity > 10) {
            discount = basePrice * 0.10; // Duplicate code
        }
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