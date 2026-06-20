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

class Developer extends Employee {
    private String project;

    public Developer(String name, String project) {
        super(name);
        this.project = project;
    }

    public String getProject() {
        return project;
    }

    public String getProjectDetails() { // Method pushed down
        return "Project: " + project + ", Status: In Progress";
    }

    // ... Developer-specific methods
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

        System.out.println(dev.getProjectDetails()); // OK
        // System.out.println(mgr.getProjectDetails()); // Compile error! Much better!
    }
}