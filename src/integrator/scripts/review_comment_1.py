import json
from pprint import pprint


real_scenario_refactoring_type = ["split variable",
                                  "extract variable",
                                  "extract function",
                                  "replace nested condition with guard clauses",
                                  "replace function with command",
                                  "consolidate condition expression",
                                  "change function declaration",
                                  "introduce assertion",
                                  "slide statments",
                                  "inline variable",
                                  "introduce special case"]



refactoring_types = dict()
refactoring_types["gpt-4o-mini"] = []
refactoring_types["deepseek"] = []
refactoring_types["gpt-4o-mini"].append({"100": ['combine functions into class', 'consolidate conditional expression', 'decompose conditional', 'encapsulate record', 'extract variable', 'pull upfield', 'pull up method', 'remove dead code', 'rename variable', 'replaceinline code with function call', 'replace nested conditional with guardclauses', 'replace parameter with query', 'split variable', 'substitute algorithm']})
refactoring_types["gpt-4o-mini"].append({"75": ['collapse hierarchy', 'extract class', 'extract function', 'extract superclass', 'inline function', 'inline variable', 'introduce parameter object', 'parameterize function', 'push down field', 'remove flag argument', 'replace conditional with polymorphism', 'replace constructor with factory function', 'replace superclass with delegate']})
refactoring_types["gpt-4o-mini"].append({"66.7": ['move statements into function', 'move statements to callers', 'renamefield', 'replace loop with pipeline', 'replace subclass with delegate', 'splitloop']})
refactoring_types["gpt-4o-mini"].append({"50": ['change reference to value', 'encapsulate collection', 'encapsulate variable', 'hide delegate', 'inline class', 'introduce special case', 'pull up constructor body', 'remove setting method', 'replace primitive with object', 'replace type code with subclasses', 'separate query from modifier']})
refactoring_types["gpt-4o-mini"].append({"33": ['replace derived variable with query', 'split phase']})
refactoring_types["gpt-4o-mini"].append({"25": ['change function declaration', 'introduce assertion', 'remove subclass', 'replace function with command', 'replace temp with query', 'slide elements']})
refactoring_types["gpt-4o-mini"].append({"0": ['change value to reference', 'combine functions into transform', 'movefield', 'move function', 'preserve whole object', 'push down method', 'remove middle man', 'replace command with function', 'replace querywith parameter']})

refactoring_types["deepseek"].append({"100": ['change function declaration', 'combine functions into class', 'consolidateconditional expression', 'decompose conditional', 'encapsulate record', 'encapsulate variable', 'extract class', 'extract function', 'extract variable', 'hide delegate', 'inline function', 'inline variable', 'introduce special case', 'move field', 'move function', 'parameterize function', 'preserve whole object', 'pull up constructor body', 'pull up field', 'pull up method', 'pushdown field', 'remove flag argument', 'remove middle man', 'remove settingmethod', 'remove subclass', 'rename field', 'replace conditional with polymorphism', 'replace constructor with factory function', 'replace functionwith command', 'replace nested condition with guard clauses', 'replaceparameter with query', 'replace superclass with delegate', 'replace tempwith query', 'separate query from modifier', 'slide elements', 'split variable', 'substitute algorithm', 'split phase', 'split loop', 'replace query withparameter', 'replace inline code with function call', 'replace derived variable with query', 'replace command with function', 'rename variable', 'remove dead code', 'move statements to callers', 'combine functions intotransform', 'replace subclass with delegate']})
refactoring_types["deepseek"].append({"75": ['change value to reference', 'collapse hierarchy', 'encapsulate collection', 'introduce assertion', 'introduce parameter object', 'push down method', 'replace primitive with object', 'replace type code with subclasses']})
refactoring_types["deepseek"].append({"66": ['replace loop with pipeline', 'move statements into function']})
refactoring_types["deepseek"].append({"50": ['change reference to value, extract superclass']})
refactoring_types["deepseek"].append({"25": ['inline class']})

def get_real_scenario_refactoring_type_with_success_ratio():
    for llm, llm_running_results in refactoring_types.items():
        print(llm)
        for llm_running_result in llm_running_results:
            for success, refactoring_type_list in  llm_running_result.items():
                if success == "100":
                    continue
                refactoring_type_list = [item for item in refactoring_type_list if item in real_scenario_refactoring_type]
                print(success, refactoring_type_list)


#get_real_scenario_refactoring_type_with_success_ratio()

code = "protected void _LOOK(@NotNull ATNState state,\n                     @Nullable ATNState stopState,\n                     @Nullable PredictionContext context,\n                     @NotNull IntervalSet lookahead,\n                     @NotNull Set<ATNConfig> lookBusy,\n                     @NotNull BitSet calledRuleStack,\n                     boolean seeThruPredicates, boolean addEOF) {\n    \n    ATNConfig config = new ATNConfig(state, 0, context);\n    \n    if (!lookBusy.add(config)) {\n        return;\n    }\n\n    if (shouldAddEpsilonToken(state, stopState, context, addEOF)) {\n        return;\n    }\n\n    if (state instanceof RuleStopState) {\n        if (context != PredictionContext.EMPTY) {\n            processReturnStates(context, stopState, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n        }\n        return;\n    }\n\n    processTransitions(state, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n}"
code1 = "private boolean shouldAddEpsilonToken(ATNState state, ATNState stopState, PredictionContext context, boolean addEOF) {\n    if (state == stopState) {\n        if (context == null) {\n            lookahead.add(Token.EPSILON);\n            return true;\n        } else if (context.isEmpty() && addEOF) {\n            lookahead.add(Token.EOF);\n            return true;\n        }\n    }\n    return false;\n}"
code2 = "private void processReturnStates(PredictionContext context, ATNState stopState, IntervalSet lookahead,\n                                  Set<ATNConfig> lookBusy, BitSet calledRuleStack,\n                                  boolean seeThruPredicates, boolean addEOF) {\n    for (int i = 0; i < context.size(); i++) {\n        ATNState returnState = atn.states.get(context.getReturnState(i));\n        boolean wasCalled = calledRuleStack.get(returnState.ruleIndex);\n        \n        try {\n            calledRuleStack.clear(returnState.ruleIndex);\n            _LOOK(returnState, stopState, context.getParent(i), lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n        } finally {\n            if (wasCalled) {\n                calledRuleStack.set(returnState.ruleIndex);\n            }\n        }\n    }\n}"
code3 = "private void processTransitions(ATNState state, ATNState stopState, PredictionContext context,\n                                 IntervalSet lookahead, Set<ATNConfig> lookBusy, BitSet calledRuleStack,\n                                 boolean seeThruPredicates, boolean addEOF) {\n    int transitionCount = state.getNumberOfTransitions();\n    \n    for (int i = 0; i < transitionCount; i++) {\n        Transition transition = state.transition(i);\n        \n        if (transition instanceof RuleTransition) {\n            handleRuleTransition((RuleTransition) transition, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n        } else if (transition instanceof PredicateTransition) {\n            handlePredicateTransition(transition, context, lookahead, seeThruPredicates);\n        } else if (transition.isEpsilon()) {\n            _LOOK(transition.target, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n        } else if (transition instanceof WildcardTransition) {\n            lookahead.addAll(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));\n        } else {\n            addLabelsToLookahead(transition, lookahead);\n        }\n    }\n}"
code4 = "private void handleRuleTransition(RuleTransition ruleTransition, ATNState stopState, PredictionContext context,\n                                   IntervalSet lookahead, Set<ATNConfig> lookBusy, BitSet calledRuleStack,\n                                   boolean seeThruPredicates, boolean addEOF) {\n    if (calledRuleStack.get(ruleTransition.target.ruleIndex)) {\n        return;\n    }\n\n    PredictionContext newContext = SingletonPredictionContext.create(context, ruleTransition.followState.stateNumber);\n    calledRuleStack.set(ruleTransition.target.ruleIndex);\n    \n    try {\n        _LOOK(ruleTransition.target, stopState, newContext, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n    } finally {\n        calledRuleStack.clear(ruleTransition.target.ruleIndex);\n    }\n}"
code5 = "private void handlePredicateTransition(Transition transition, PredictionContext context, IntervalSet lookahead, boolean seeThruPredicates) {\n    if (seeThruPredicates) {\n        _LOOK(transition.target, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);\n    } else {\n        lookahead.add(HIT_PRED);\n    }\n}"
code6 = "private void addLabelsToLookahead(Transition transition, IntervalSet lookahead) {\n    IntervalSet labels = transition.label();\n    if (labels != null) {\n        if (transition instanceof NotSetTransition) {\n            labels = labels.complement(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));\n        }\n        lookahead.addAll(labels);\n    }\n}"
code7 = " protected void _LOOK(@NotNull ATNState s,\n\t\t\t\t\t\t @Nullable ATNState stopState,\n\t\t\t\t\t\t @Nullable PredictionContext ctx,\n\t\t\t\t\t\t @NotNull IntervalSet look,\n                         @NotNull Set<ATNConfig> lookBusy,\n\t\t\t\t\t\t @NotNull BitSet calledRuleStack,\n\t\t\t\t\t\t boolean seeThruPreds, boolean addEOF)\n\t{\n//\t\tSystem.out.println(\"_LOOK(\"+s.stateNumber+\", ctx=\"+ctx);\n        ATNConfig c = new ATNConfig(s, 0, ctx);\n        if ( !lookBusy.add(c) ) return;\n\n\t\tif (s == stopState) {\n\t\t\tif (ctx == null) {\n\t\t\t\tlook.add(Token.EPSILON);\n\t\t\t\treturn;\n\t\t\t} else if (ctx.isEmpty() && addEOF) {\n\t\t\t\tlook.add(Token.EOF);\n\t\t\t\treturn;\n\t\t\t}\n\t\t}\n\n        if ( s instanceof RuleStopState ) {\n            if ( ctx==null ) {\n                look.add(Token.EPSILON);\n                return;\n            } else if (ctx.isEmpty() && addEOF) {\n\t\t\t\tlook.add(Token.EOF);\n\t\t\t\treturn;\n\t\t\t}\n\n\t\t\tif ( ctx != PredictionContext.EMPTY ) {\n\t\t\t\t// run thru all possible stack tops in ctx\n\t\t\t\tfor (int i = 0; i < ctx.size(); i++) {\n\t\t\t\t\tATNState returnState = atn.states.get(ctx.getReturnState(i));\n//\t\t\t\t\tSystem.out.println(\"popping back to \"+retState);\n\n\t\t\t\t\tboolean removed = calledRuleStack.get(returnState.ruleIndex);\n\t\t\t\t\ttry {\n\t\t\t\t\t\tcalledRuleStack.clear(returnState.ruleIndex);\n\t\t\t\t\t\t_LOOK(returnState, stopState, ctx.getParent(i), look, lookBusy, calledRuleStack, seeThruPreds, addEOF);\n\t\t\t\t\t}\n\t\t\t\t\tfinally {\n\t\t\t\t\t\tif (removed) {\n\t\t\t\t\t\t\tcalledRuleStack.set(returnState.ruleIndex);\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t\treturn;\n\t\t\t}\n        }\n\n        int n = s.getNumberOfTransitions();\n        for (int i=0; i<n; i++) {\n\t\t\tTransition t = s.transition(i);\n\t\t\tif ( t.getClass() == RuleTransition.class ) {\n\t\t\t\tif (calledRuleStack.get(((RuleTransition)t).target.ruleIndex)) {\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\n\t\t\t\tPredictionContext newContext =\n\t\t\t\t\tSingletonPredictionContext.create(ctx, ((RuleTransition)t).followState.stateNumber);\n\n\t\t\t\ttry {\n\t\t\t\t\tcalledRuleStack.set(((RuleTransition)t).target.ruleIndex);\n\t\t\t\t\t_LOOK(t.target, stopState, newContext, look, lookBusy, calledRuleStack, seeThruPreds, addEOF);\n\t\t\t\t}\n\t\t\t\tfinally {\n\t\t\t\t\tcalledRuleStack.clear(((RuleTransition)t).target.ruleIndex);\n\t\t\t\t}\n\t\t\t}\n\t\t\telse if ( t instanceof PredicateTransition ) {\n\t\t\t\tif ( seeThruPreds ) {\n\t\t\t\t\t_LOOK(t.target, stopState, ctx, look, lookBusy, calledRuleStack, seeThruPreds, addEOF);\n\t\t\t\t}\n\t\t\t\telse {\n\t\t\t\t\tlook.add(HIT_PRED);\n\t\t\t\t}\n\t\t\t}\n\t\t\telse if ( t.isEpsilon() ) {\n\t\t\t\t_LOOK(t.target, stopState, ctx, look, lookBusy, calledRuleStack, seeThruPreds, addEOF);\n\t\t\t}\n\t\t\telse if ( t.getClass() == WildcardTransition.class ) {\n\t\t\t\tlook.addAll( IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType) );\n\t\t\t}\n\t\t\telse {\n//\t\t\t\tSystem.out.println(\"adding \"+ t);\n\t\t\t\tIntervalSet set = t.label();\n\t\t\t\tif (set != null) {\n\t\t\t\t\tif (t instanceof NotSetTransition) {\n\t\t\t\t\t\tset = set.complement(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));\n\t\t\t\t\t}\n\t\t\t\t\tlook.addAll(set);\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}"
print(code7)
print("="*50, "Refactoring 1", "="*50)
print(code)
print("="*50, "Refactoring 1", "="*50)
print(code1)
print("="*50, "Refactoring 2", "="*50)
print(code2)
print("="*50, "Refactoring 3", "="*50)
print(code3)
print("="*50, "Refactoring 4", "="*50)
print(code4)
print("="*50, "Refactoring 5", "="*50)
print(code5)
print("="*50, "Refactoring 6", "="*50)
print(code6)
print("="*50, "Refactoring 7", "="*50)


