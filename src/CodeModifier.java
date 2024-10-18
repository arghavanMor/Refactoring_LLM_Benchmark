package org.refactoring;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import java.io.*;


public class CodeModifier {

    public static Boolean codeModifier(String pathClass, String methodName, String newMethodCode) throws FileNotFoundException {
        File projectDir = new File(pathClass);

        CompilationUnit compilationUnitNode = StaticJavaParser.parse(projectDir);

        // Define a new method to replace the old one
        MethodDeclaration newMethod = StaticJavaParser.parseMethodDeclaration(newMethodCode);

        // Find and replace the original method
        compilationUnitNode.findAll(ClassOrInterfaceDeclaration.class).forEach(eachClass -> {
            eachClass.getMethodsByName(methodName).forEach(method -> {
                method.replace(newMethod);
            });
        });

        try (FileWriter fileWriter = new FileWriter(projectDir)) {
            fileWriter.write(compilationUnitNode.toString());
         } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return true;

    }

    public static void main(String[] args) throws FileNotFoundException {
        String pathClass = args[0];
        String methodName = args[1];
        String newMethodCode = args[2];

        System.out.println("----------------- The jar file is being called -----------------");
        codeModifier(pathClass, methodName, newMethodCode);
        System.out.println(" -------------------------- Finished ---------------------------");
    }
}


