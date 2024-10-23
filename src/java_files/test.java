void receive(Object object) {
    if (object instanceof ObjectTypeA) {
        doSomethingA();
    }
    else {
        if (object instanceof ObjectTypeB) {
            doSomethingB();
        }
        else {
            if (object instanceof ObjectTypeC) {
                doSomethingC();
            }
            else {
                if (object instanceof ObjectTypeD) {
                    doSomethingD();
                }
                else {
                    // etc...
                }
            }
        }
    }
}