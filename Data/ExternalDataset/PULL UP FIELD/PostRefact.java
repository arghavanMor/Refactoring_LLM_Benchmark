class Employee {
    private String name;
    private String department; // Field pulled up

    public Employee(String name, String department) {
        this.name = name;
        this.department = department;
    }

    public String getName() {
        return name;
    }

    public String getDepartment() {
        return department;
    }

    // ... other methods (potentially moved from subclasses)
}

class Manager extends Employee {
    public Manager(String name, String department) {
        super(name, department); // Call superclass constructor
    }

    // ... other Manager-specific methods
}

class Developer extends Employee {
    public Developer(String name, String department) {
        super(name, department); // Call superclass constructor
    }

    // ... other Developer-specific methods
}

public class Main {
    public static void main(String[] args) {
        Manager mgr = new Manager("Alice", "Sales");
        Developer dev = new Developer("Bob", "Development");

        System.out.println(mgr.getDepartment());
        System.out.println(dev.getDepartment());
    }
}