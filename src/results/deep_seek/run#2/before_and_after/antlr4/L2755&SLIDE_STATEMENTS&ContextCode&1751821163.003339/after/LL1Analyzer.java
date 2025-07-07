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

import org.antlr.v4.runtime.RuleContext;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.misc.IntervalSet;
import org.antlr.v4.runtime.misc.NotNull;
import org.antlr.v4.runtime.misc.Nullable;
import java.util.BitSet;
import java.util.HashSet;
import java.util.Set;

public class LL1Analyzer {

    /**
     * Special value added to the lookahead sets to indicate that we hit
     *  a predicate during analysis if {@code seeThruPreds==false}.
     */
    public static final int HIT_PRED = Token.INVALID_TYPE;

    @NotNull
    public final ATN atn;

    public LL1Analyzer(@NotNull ATN atn) {
        this.atn = atn;
    }

    /**
     * Calculates the SLL(1) expected lookahead set for each outgoing transition
     * of an {@link ATNState}. The returned array has one element for each
     * outgoing transition in {@code s}. If the closure from transition
     * <em>i</em> leads to a semantic predicate before matching a symbol, the
     * element at index <em>i</em> of the result will be {@code null}.
     *
     * @param s the ATN state
     * @return the expected symbols for each outgoing transition of {@code s}.
     */
    @Nullable
    public IntervalSet[] getDecisionLookahead(@Nullable ATNState s) {
        // System.out.println("LOOK("+s.stateNumber+")");
        if (s == null) {
            return null;
        }
        IntervalSet[] look = new IntervalSet[s.getNumberOfTransitions()];
        for (int alt = 0; alt < s.getNumberOfTransitions(); alt++) {
            look[alt] = new IntervalSet();
            Set<ATNConfig> lookBusy = new HashSet<ATNConfig>();
            // fail to get lookahead upon pred
            boolean seeThruPreds = false;
            _LOOK(s.transition(alt).target, null, PredictionContext.EMPTY, look[alt], lookBusy, new BitSet(), seeThruPreds, false);
            // Wipe out lookahead for this alternative if we found nothing
            // or we had a predicate when we !seeThruPreds
            if (look[alt].size() == 0 || look[alt].contains(HIT_PRED)) {
                look[alt] = null;
            }
        }
        return look;
    }

    /**
     * Compute set of tokens that can follow {@code s} in the ATN in the
     * specified {@code ctx}.
     * <p/>
     * If {@code ctx} is {@code null} and the end of the rule containing
     * {@code s} is reached, {@link Token#EPSILON} is added to the result set.
     * If {@code ctx} is not {@code null} and the end of the outermost rule is
     * reached, {@link Token#EOF} is added to the result set.
     *
     * @param s the ATN state
     * @param ctx the complete parser context, or {@code null} if the context
     * should be ignored
     *
     * @return The set of tokens that can follow {@code s} in the ATN in the
     * specified {@code ctx}.
     */
    @NotNull
    public IntervalSet LOOK(@NotNull ATNState s, @Nullable RuleContext ctx) {
        return LOOK(s, null, ctx);
    }

    /**
     * Compute set of tokens that can follow {@code s} in the ATN in the
     * specified {@code ctx}.
     * <p/>
     * If {@code ctx} is {@code null} and the end of the rule containing
     * {@code s} is reached, {@link Token#EPSILON} is added to the result set.
     * If {@code ctx} is not {@code null} and the end of the outermost rule is
     * reached, {@link Token#EOF} is added to the result set.
     *
     * @param s the ATN state
     * @param stopState the ATN state to stop at. This can be a
     * {@link BlockEndState} to detect epsilon paths through a closure.
     * @param ctx the complete parser context, or {@code null} if the context
     * should be ignored
     *
     * @return The set of tokens that can follow {@code s} in the ATN in the
     * specified {@code ctx}.
     */
    @NotNull
    public IntervalSet LOOK(@NotNull ATNState s, @Nullable ATNState stopState, @Nullable RuleContext ctx) {
        IntervalSet r = new IntervalSet();
        // ignore preds; get all lookahead
        boolean seeThruPreds = true;
        PredictionContext lookContext = ctx != null ? PredictionContext.fromRuleContext(s.atn, ctx) : null;
        _LOOK(s, stopState, lookContext, r, new HashSet<ATNConfig>(), new BitSet(), seeThruPreds, true);
        return r;
    }

    protected void look(@NotNull ATNState state, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, @NotNull Set<ATNConfig> lookBusy, @NotNull BitSet calledRuleStack, boolean seeThroughPredicates, boolean addEOF) {
        ATNConfig config = new ATNConfig(state, 0, context);
        if (!lookBusy.add(config))
            return;
        handleStopState(state, stopState, context, lookahead, addEOF);
        if (state instanceof RuleStopState) {
            handleRuleStopState(context, stopState, lookahead, calledRuleStack, seeThroughPredicates, addEOF);
            return;
        }
        processTransitions(state, stopState, context, lookahead, lookBusy, calledRuleStack, seeThroughPredicates, addEOF);
    }

    private void handleStopState(@NotNull ATNState state, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, boolean addEOF) {
        if (state == stopState) {
            if (context == null) {
                lookahead.add(Token.EPSILON);
            } else if (context.isEmpty() && addEOF) {
                lookahead.add(Token.EOF);
            }
        }
    }

    private void handleRuleStopState(@Nullable PredictionContext context, @Nullable ATNState stopState, @NotNull IntervalSet lookahead, @NotNull BitSet calledRuleStack, boolean seeThroughPredicates, boolean addEOF) {
        if (context == null) {
            lookahead.add(Token.EPSILON);
        } else if (context.isEmpty() && addEOF) {
            lookahead.add(Token.EOF);
        }
        if (context != PredictionContext.EMPTY) {
            for (int i = 0; i < context.size(); i++) {
                ATNState returnState = atn.states.get(context.getReturnState(i));
                boolean removed = calledRuleStack.get(returnState.ruleIndex);
                try {
                    calledRuleStack.clear(returnState.ruleIndex);
                    look(returnState, stopState, context.getParent(i), lookahead, lookBusy, calledRuleStack, seeThroughPredicates, addEOF);
                } finally {
                    if (removed) {
                        calledRuleStack.set(returnState.ruleIndex);
                    }
                }
            }
        }
    }

    private void processTransitions(@NotNull ATNState state, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, @NotNull Set<ATNConfig> lookBusy, @NotNull BitSet calledRuleStack, boolean seeThroughPredicates, boolean addEOF) {
        int numberOfTransitions = state.getNumberOfTransitions();
        for (int i = 0; i < numberOfTransitions; i++) {
            Transition transition = state.transition(i);
            handleTransition(transition, stopState, context, lookahead, lookBusy, calledRuleStack, seeThroughPredicates, addEOF);
        }
    }

    private void handleTransition(Transition transition, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, @NotNull Set<ATNConfig> lookBusy, @NotNull BitSet calledRuleStack, boolean seeThroughPredicates, boolean addEOF) {
        if (transition instanceof RuleTransition) {
            processRuleTransition((RuleTransition) transition, stopState, context, lookahead, calledRuleStack, seeThroughPredicates, addEOF);
        } else if (transition instanceof PredicateTransition) {
            processPredicateTransition(transition, stopState, context, lookahead, seeThroughPredicates, addEOF);
        } else if (transition.isEpsilon()) {
            look(transition.target, stopState, context, lookahead, lookBusy, calledRuleStack, seeThroughPredicates, addEOF);
        } else if (transition instanceof WildcardTransition) {
            lookahead.addAll(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));
        } else {
            processOtherTransitions(transition, lookahead);
        }
    }

    private void processRuleTransition(RuleTransition transition, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, @NotNull BitSet calledRuleStack, boolean seeThroughPredicates, boolean addEOF) {
        if (calledRuleStack.get(transition.target.ruleIndex))
            return;
        PredictionContext newContext = SingletonPredictionContext.create(context, transition.followState.stateNumber);
        try {
            calledRuleStack.set(transition.target.ruleIndex);
            look(transition.target, stopState, newContext, lookahead, lookBusy, calledRuleStack, seeThroughPredicates, addEOF);
        } finally {
            calledRuleStack.clear(transition.target.ruleIndex);
        }
    }

    private void processPredicateTransition(Transition transition, @Nullable ATNState stopState, @Nullable PredictionContext context, @NotNull IntervalSet lookahead, boolean seeThroughPredicates, boolean addEOF) {
        if (seeThroughPredicates) {
            look(transition.target, stopState, context, lookahead, lookBusy, calledRuleStack, seeThroughPredicates, addEOF);
        } else {
            lookahead.add(HIT_PRED);
        }
    }

    private void processOtherTransitions(Transition transition, @NotNull IntervalSet lookahead) {
        IntervalSet set = transition.label();
        if (set != null) {
            if (transition instanceof NotSetTransition) {
                set = set.complement(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));
            }
            lookahead.addAll(set);
        }
    }
}
