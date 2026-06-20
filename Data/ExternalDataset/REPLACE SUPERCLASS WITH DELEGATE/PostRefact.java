class Person { // Remains unchanged
    private String name;
    private String address;

    public Person(String name, String address) {
        this.name = name;
        this.address = address;
    }

    public String getName() {
        return name;
    }

    public String getAddress() {
        return address;
    }

    public String getContactInfo() {
        return name + ", " + address;
    }

    // ... many other methods related to a person
}

class Employee {
    private Person person; // Delegate
    private String employeeId;

    public Employee(String name, String address, String employeeId) {
        this.person = new Person(name, address); // Create the delegate
        this.employeeId = employeeId;
    }

    public String getName() {
        return person.getName(); // Forward the call to the delegate
    }

    public String getEmployeeId() {
        return employeeId;
    }

    // No longer inherits getAddress or other Person methods.
}

public class Main {
    public static void main(String[] args) {
        Employee emp = new Employee("Alice", "123 Main St", "E12345");
        System.out.println(emp.getName());
        System.out.println(emp.getEmployeeId());
    }
}