/*
 * [The "BSD license"]
 *  Copyright (c) 2012 Terence Parr
 *  Copyright (c) 2012 Sam Harwell
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *  1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *  3. The name of the author may not be used to endorse or promote products
 *     derived from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 *  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 *  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 *  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 *  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 *  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package org.antlr.v4.runtime.atn;

import org.antlr.v4.runtime.IntStream;
import org.antlr.v4.runtime.RuleContext;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.misc.IntervalSet;
import org.antlr.v4.runtime.misc.NotNull;
import org.antlr.v4.runtime.misc.Nullable;
import java.util.HashSet;
import java.util.Set;

public class LL1Analyzer {

    /**
     * Special value added to the lookahead sets to indicate that we hit
     *  a predicate during analysis if seeThruPreds==false.
     */
    public static final int HIT_PRED = Token.INVALID_TYPE;

    @NotNull
    public final ATN atn;

    public LL1Analyzer(@NotNull ATN atn) {
        this.atn = atn;
    }

    /**
     * From an ATN state, {@code s}, find the set of all labels reachable from
     * {@code s} at depth k. Only for DecisionStates.
     */
    @Nullable
    public IntervalSet[] getDecisionLookahead(@Nullable ATNState s) {
        // System.out.println("LOOK("+s.stateNumber+")");
        if (s == null)
            return null;
        IntervalSet[] look = new IntervalSet[s.getNumberOfTransitions() + 1];
        for (int alt = 1; alt <= s.getNumberOfTransitions(); alt++) {
            look[alt] = new IntervalSet();
            Set<ATNConfig> lookBusy = new HashSet<ATNConfig>();
            // fail to get lookahead upon pred
            boolean seeThruPreds = false;
            _LOOK(s.transition(alt - 1).target, PredictionContext.EMPTY, look[alt], lookBusy, seeThruPreds, false);
            // Wipe out lookahead for this alternative if we found nothing
            // or we had a predicate when we !seeThruPreds
            if (look[alt].size() == 0 || look[alt].contains(HIT_PRED)) {
                look[alt] = null;
            }
        }
        return look;
    }

    /**
     * Get lookahead, using {@code ctx} if we reach end of rule. If {@code ctx}
     * is {@code null} or {@link RuleContext#EMPTY EMPTY}, don't chase FOLLOW.
     * If {@code ctx} is {@code null}, {@link Token#EPSILON EPSILON} is in set
     * if we can reach end of rule. If {@code ctx} is
     * {@link RuleContext#EMPTY EMPTY}, {@link IntStream#EOF EOF} is in set if
     * we can reach end of rule.
     */
    @NotNull
    public IntervalSet LOOK(@NotNull ATNState s, @Nullable RuleContext ctx) {
        IntervalSet r = new IntervalSet();
        // ignore preds; get all lookahead
        boolean seeThruPreds = true;
        PredictionContext lookContext = ctx != null ? PredictionContext.fromRuleContext(s.atn, ctx) : null;
        _LOOK(s, lookContext, r, new HashSet<ATNConfig>(), seeThruPreds, true);
        return r;
    }

    protected void _LOOK(@NotNull ATNState state, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, @NotNull Set<ATNConfig> lookBusy, @NotNull BitSet calledRuleStack, boolean seeThruPredicates, boolean addEOF) {
        ATNConfig config = new ATNConfig(state, 0, context);
        if (!lookBusy.add(config)) {
            return;
        }
        if (shouldAddEpsilonToken(state, stopState, context, addEOF)) {
            return;
        }
        if (state instanceof RuleStopState) {
            if (context != PredictionContext.EMPTY) {
                processReturnStates(context, stopState, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
            }
            return;
        }
        processTransitions(state, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
    }

    private boolean shouldAddEpsilonToken(ATNState state, ATNState stopState, PredictionContext context, boolean addEOF) {
        if (state == stopState) {
            if (context == null) {
                lookahead.add(Token.EPSILON);
                return true;
            } else if (context.isEmpty() && addEOF) {
                lookahead.add(Token.EOF);
                return true;
            }
        }
        return false;
    }

    private void processReturnStates(PredictionContext context, ATNState stopState, IntervalSet lookahead, Set<ATNConfig> lookBusy, BitSet calledRuleStack, boolean seeThruPredicates, boolean addEOF) {
        for (int i = 0; i < context.size(); i++) {
            ATNState returnState = atn.states.get(context.getReturnState(i));
            boolean wasCalled = calledRuleStack.get(returnState.ruleIndex);
            try {
                calledRuleStack.clear(returnState.ruleIndex);
                _LOOK(returnState, stopState, context.getParent(i), lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
            } finally {
                if (wasCalled) {
                    calledRuleStack.set(returnState.ruleIndex);
                }
            }
        }
    }

    private void processTransitions(ATNState state, ATNState stopState, PredictionContext context, IntervalSet lookahead, Set<ATNConfig> lookBusy, BitSet calledRuleStack, boolean seeThruPredicates, boolean addEOF) {
        int transitionCount = state.getNumberOfTransitions();
        for (int i = 0; i < transitionCount; i++) {
            Transition transition = state.transition(i);
            if (transition instanceof RuleTransition) {
                handleRuleTransition((RuleTransition) transition, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
            } else if (transition instanceof PredicateTransition) {
                handlePredicateTransition(transition, context, lookahead, seeThruPredicates);
            } else if (transition.isEpsilon()) {
                _LOOK(transition.target, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
            } else if (transition instanceof WildcardTransition) {
                lookahead.addAll(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));
            } else {
                addLabelsToLookahead(transition, lookahead);
            }
        }
    }

    private void handleRuleTransition(RuleTransition ruleTransition, ATNState stopState, PredictionContext context, IntervalSet lookahead, Set<ATNConfig> lookBusy, BitSet calledRuleStack, boolean seeThruPredicates, boolean addEOF) {
        if (calledRuleStack.get(ruleTransition.target.ruleIndex)) {
            return;
        }
        PredictionContext newContext = SingletonPredictionContext.create(context, ruleTransition.followState.stateNumber);
        calledRuleStack.set(ruleTransition.target.ruleIndex);
        try {
            _LOOK(ruleTransition.target, stopState, newContext, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
        } finally {
            calledRuleStack.clear(ruleTransition.target.ruleIndex);
        }
    }

    private void handlePredicateTransition(Transition transition, PredictionContext context, IntervalSet lookahead, boolean seeThruPredicates) {
        if (seeThruPredicates) {
            _LOOK(transition.target, stopState, context, lookahead, lookBusy, calledRuleStack, seeThruPredicates, addEOF);
        } else {
            lookahead.add(HIT_PRED);
        }
    }

    private void addLabelsToLookahead(Transition transition, IntervalSet lookahead) {
        IntervalSet labels = transition.label();
        if (labels != null) {
            if (transition instanceof NotSetTransition) {
                labels = labels.complement(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));
            }
            lookahead.addAll(labels);
        }
    }
}
