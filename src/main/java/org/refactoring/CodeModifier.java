package org.refactoring;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.BodyDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;


public class CodeModifier {

    public static Boolean codeModifier(String pathClass, String mainMethodName, String mainMethodCode, ArrayList<String> otherMethodsCode, ArrayList<String> classesCode, ArrayList<String> otherCode) throws FileNotFoundException {
        File projectDir = new File(pathClass);

        /*
        System.out.println("----------------------------------------");
        System.out.println(pathClass);
        System.out.println("----------------------------------------");
        System.out.println(mainMethodName);
        System.out.println("----------------------------------------");
        System.out.println(mainMethodCode);
        System.out.println("----------------------------------------");
        System.out.println(otherMethodsCode.toString());
        System.out.println("----------------------------------------");
        System.out.println(classesCode.toString());
        System.out.println("----------------------------------------");
        System.out.println(otherCode.toString());
        System.out.println("----------------------------------------");
        */

        CompilationUnit compilationUnitNode = StaticJavaParser.parse(projectDir);
        MethodDeclaration mainMethod = StaticJavaParser.parseMethodDeclaration(mainMethodCode);
        compilationUnitNode.findAll(ClassOrInterfaceDeclaration.class).forEach(eachClass -> {
            eachClass.getMethodsByName(mainMethodName).forEach(method -> {
                System.out.println("----------------- Refactoring starting  -----------------");
                method.replace(mainMethod);

                for (String otherMethodCode : otherMethodsCode) {
                    if (!otherMethodCode.isEmpty()){
                        MethodDeclaration otherMethod = StaticJavaParser.parseMethodDeclaration(otherMethodCode);
                        {
                            eachClass.addMember(otherMethod);
                        }
                    }
                }

                for (String classCode : classesCode) {
                    if (!classCode.isEmpty()){
                        BodyDeclaration<?> innerClass = StaticJavaParser.parseBodyDeclaration(classCode);
                        if (innerClass instanceof ClassOrInterfaceDeclaration) {
                            eachClass.addMember(innerClass);
                        }
                    }
                }
                System.out.println("----------------- Refactoring process terminated -----------------");
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
        String mainMethodName = args[1];
        String mainMethodCode = args[2];
        String otherMethodsCodeArg = args[3];
        String classesCodeArg = args[4];
        ArrayList<String> otherCode = new ArrayList<>();

        ArrayList<String> otherMethodsCode = new ArrayList<>(Arrays.asList(otherMethodsCodeArg.split("/* */")));
        otherMethodsCode.removeIf(str -> str.equals("* *"));

        ArrayList<String> classesCode = new ArrayList<>(Arrays.asList(classesCodeArg.split("/* */")));
        classesCode.removeIf(str -> str.equals("* *"));

        codeModifier(pathClass, mainMethodName, mainMethodCode, otherMethodsCode, classesCode, otherCode);
    }
}


