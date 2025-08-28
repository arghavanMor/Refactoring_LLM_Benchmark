class Employee {
    private String name;

    public Employee(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    // ... other methods
}

class Manager extends Employee {
    private String department; // Field to be pulled up

    public Manager(String name, String department) {
        super(name);
        this.department = department;
    }

    public String getDepartment() {
        return department;
    }

    // ... other methods that use department
}

class Developer extends Employee {
    private String department; // Duplicate field

    public Developer(String name, String department) {
        super(name);
        this.department = department;
    }

    public String getDepartment() {
        return department;
    }

    // ... other methods that use department
}

public class Main {
    public static void main(String[] args) {
        Manager mgr = new Manager("Alice", "Sales");
        Developer dev = new Developer("Bob", "Development");

        System.out.println(mgr.getDepartment());
        System.out.println(dev.getDepartment());
    }
}