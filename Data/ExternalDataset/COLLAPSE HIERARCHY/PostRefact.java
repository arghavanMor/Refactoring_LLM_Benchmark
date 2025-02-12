class Animal {
    private String name;
    private boolean canWagTail; // Added flag

    public Animal(String name, boolean canWagTail) {
        this.name = name;
        this.canWagTail = canWagTail;
    }

    public String getName() {
        return name;
    }

    public void makeSound() {
        System.out.println("Generic animal sound");
    }

    public void makeSound(boolean isDog) { // Overloaded method
        if (isDog) {
            System.out.println("Woof!");
        } else {
            System.out.println("Generic animal sound");
        }
    }


    public void wagTail() {
        if (canWagTail) {
            System.out.println("Tail wagging");
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Animal myDog = new Animal("Buddy", true); // Dog can wag tail
        myDog.makeSound(true); // Call dog sound
        myDog.wagTail();

        Animal myAnimal = new Animal("Generic", false); // Generic animal can't wag
        myAnimal.makeSound(false);
    }
}