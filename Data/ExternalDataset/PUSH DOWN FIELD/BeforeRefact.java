class Employee {
    private String name;
    private String project; // Field to be pushed down

    public Employee(String name, String project) {
        this.name = name;
        this.project = project;
    }

    public String getName() {
        return name;
    }

    public String getProject() {
        return project;
    }

    //... other methods, some of which use 'project'
}

class Developer extends Employee {
    public Developer(String name, String project) {
        super(name, project);
    }

    //... Developer-specific methods that use 'project'
}

class Manager extends Employee {
    public Manager(String name) {
        super(name, null); // Managers don't have a project
    }

    //... Manager-specific methods (don't use 'project')
}

public class Main {
    public static void main(String args) {
        Developer dev = new Developer("Bob", "Cool Project");
        Manager mgr = new Manager("Alice");

        System.out.println(dev.getProject()); // OK
        System.out.println(mgr.getProject()); // Null, not ideal
    }
}