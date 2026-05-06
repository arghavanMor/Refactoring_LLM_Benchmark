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

    protected void calculateLookahead(@NotNull ATNState state, @Nullable PredictionContext context, @NotNull IntervalSet lookaheadSet, @NotNull Set<ATNConfig> visitedConfigs, boolean traversePredicates, boolean includeEOF) {
        ATNConfig config = new ATNConfig(state, 0, context);
        if (!visitedConfigs.add(config))
            return;
        if (state instanceof RuleStopState) {
            if (context == null) {
                lookaheadSet.add(Token.EPSILON);
                return;
            } else if (context.isEmpty() && includeEOF) {
                lookaheadSet.add(Token.EOF);
                return;
            }
            if (context != PredictionContext.EMPTY) {
                for (SingletonPredictionContext prediction : context) {
                    ATNState returnState = atn.states.get(prediction.returnState);
                    calculateLookahead(returnState, prediction.parent, lookaheadSet, visitedConfigs, traversePredicates, includeEOF);
                }
                return;
            }
        }
        int transitionCount = state.getNumberOfTransitions();
        for (int i = 0; i < transitionCount; i++) {
            Transition transition = state.transition(i);
            if (transition.getClass() == RuleTransition.class) {
                PredictionContext newContext = SingletonPredictionContext.create(context, ((RuleTransition) transition).followState.stateNumber);
                calculateLookahead(transition.target, newContext, lookaheadSet, visitedConfigs, traversePredicates, includeEOF);
            } else if (transition instanceof PredicateTransition) {
                if (traversePredicates) {
                    calculateLookahead(transition.target, context, lookaheadSet, visitedConfigs, traversePredicates, includeEOF);
                } else {
                    lookaheadSet.add(HIT_PRED);
                }
            } else if (transition.isEpsilon()) {
                calculateLookahead(transition.target, context, lookaheadSet, visitedConfigs, traversePredicates, includeEOF);
            } else if (transition.getClass() == WildcardTransition.class) {
                lookaheadSet.addAll(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));
            } else {
                IntervalSet labelSet = transition.label();
                if (labelSet != null) {
                    if (transition instanceof NotSetTransition) {
                        labelSet = labelSet.complement(IntervalSet.of(Token.MIN_USER_TOKEN_TYPE, atn.maxTokenType));
                    }
                    lookaheadSet.addAll(labelSet);
                }
            }
        }
    }
}
