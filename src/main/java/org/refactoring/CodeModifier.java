package org.refactoring;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.BodyDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import java.io.*;



public class CodeModifier {

    public static Boolean codeModifier(String pathClass, String methodName, String newMethodCode, String classCode, String otherCode) throws FileNotFoundException {
        File projectDir = new File(pathClass);

        System.out.println("----------------------------------------");
        System.out.println(pathClass);
        System.out.println("----------------------------------------");
        System.out.println(methodName);
        System.out.println("----------------------------------------");
        System.out.println(newMethodCode);
        System.out.println("----------------------------------------");
        System.out.println(classCode);
        System.out.println("----------------------------------------");
        System.out.println(otherCode);
        System.out.println("----------------------------------------");

        /*
        CompilationUnit compilationUnitNode = StaticJavaParser.parse(projectDir);
        // Define a new method to replace the old one
        MethodDeclaration newMethod = StaticJavaParser.parseMethodDeclaration(newMethodCode);
        // Find and replace the original method
        compilationUnitNode.findAll(ClassOrInterfaceDeclaration.class).forEach(eachClass -> {
            eachClass.getMethodsByName(methodName).forEach(method -> {
                System.out.printf("----------------- %s is refactoring -----------------", methodName);
                method.replace(newMethod);

                if (!classCode.isEmpty()){
                    BodyDeclaration<?> innerClass = StaticJavaParser.parseBodyDeclaration(classCode);
                    if (innerClass instanceof ClassOrInterfaceDeclaration) {
                      eachClass.addMember((ClassOrInterfaceDeclaration) innerClass);
                        System.out.printf("----------------- Inner class added to %s -----------------", eachClass);
                    }
                }
            });
        });

        try (FileWriter fileWriter = new FileWriter(projectDir)) {
            fileWriter.write(compilationUnitNode.toString());
         } catch (IOException e) {
            throw new RuntimeException(e);
        }
        */
        return true;

    }


    public static void main(String[] args) throws FileNotFoundException {
        //String pathClass = args[0];
        //String methodName = args[1];
        //String newMethodCode = args[2];
        //String classCode = args[3];
        //String otherCode = args[4];
        System.out.println("----------------- Refactoring process has started .... -----------------");
        Boolean result = codeModifier(pathClass, methodName, newMethodCode, classCode, otherCode);
        //System.out.println(result);
        System.out.println(" -------------------------- Refactoring process terminated .... ---------------------------");
        //return result;
    }
}


