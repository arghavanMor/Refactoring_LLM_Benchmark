class Person {
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

class Employee extends Person {
    private String employeeId;

    public Employee(String name, String address, String employeeId) {
        super(name, address);
        this.employeeId = employeeId;
    }

    public String getEmployeeId() {
        return employeeId;
    }

    // Employee only really needs getName() and getEmployeeId()
    // but inherits all of Person's methods, some of which are irrelevant.
}

public class Main {
    public static void main(String[] args) {
        Employee emp = new Employee("Alice", "123 Main St", "E12345");
        System.out.println(emp.getName());
        System.out.println(emp.getEmployeeId());
        // emp.getAddress(); // Might not be needed.
    }
}