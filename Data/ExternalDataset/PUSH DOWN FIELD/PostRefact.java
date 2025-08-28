class Employee {
    private String name;

    public Employee(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    // ... other methods (no longer use 'project')
}

class Developer extends Employee {
    private String project; // Field pushed down

    public Developer(String name, String project) {
        super(name);
        this.project = project;
    }

    public String getProject() {
        return project;
    }

    // ... Developer-specific methods that use 'project'
}

class Manager extends Employee {
    public Manager(String name) {
        super(name);
    }

    // ... Manager-specific methods
}

public class Main {
    public static void main(String[] args) {
        Developer dev = new Developer("Bob", "Cool Project");
        Manager mgr = new Manager("Alice");

        System.out.println(dev.getProject()); // OK
        // System.out.println(mgr.getProject()); // Compile error!  Much better!
    }
}