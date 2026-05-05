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
package org.antlr.v4.tool;

import org.antlr.v4.misc.Utils;
import org.antlr.v4.runtime.atn.ATNConfig;
import org.antlr.v4.runtime.atn.ATNState;
import org.antlr.v4.runtime.atn.AbstractPredicateTransition;
import org.antlr.v4.runtime.atn.ActionTransition;
import org.antlr.v4.runtime.atn.AtomTransition;
import org.antlr.v4.runtime.atn.BlockEndState;
import org.antlr.v4.runtime.atn.BlockStartState;
import org.antlr.v4.runtime.atn.DecisionState;
import org.antlr.v4.runtime.atn.NotSetTransition;
import org.antlr.v4.runtime.atn.PlusBlockStartState;
import org.antlr.v4.runtime.atn.PlusLoopbackState;
import org.antlr.v4.runtime.atn.RangeTransition;
import org.antlr.v4.runtime.atn.RuleStopState;
import org.antlr.v4.runtime.atn.RuleTransition;
import org.antlr.v4.runtime.atn.SetTransition;
import org.antlr.v4.runtime.atn.StarBlockStartState;
import org.antlr.v4.runtime.atn.StarLoopEntryState;
import org.antlr.v4.runtime.atn.StarLoopbackState;
import org.antlr.v4.runtime.atn.Transition;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.dfa.DFAState;
import org.antlr.v4.runtime.misc.IntegerList;
import org.stringtemplate.v4.ST;
import org.stringtemplate.v4.STGroup;
import org.stringtemplate.v4.STGroupFile;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

/**
 * The DOT (part of graphviz) generation aspect.
 */
public class DOTGenerator {

    public static final boolean STRIP_NONREDUCED_STATES = false;

    protected String arrowhead = "normal";

    protected String rankdir = "LR";

    /**
     * Library of output templates; use {@code <attrname>} format.
     */
    public static STGroup stlib = new STGroupFile("org/antlr/v4/tool/templates/dot/graphs.stg");

    protected Grammar grammar;

    /**
     * This aspect is associated with a grammar
     */
    public DOTGenerator(Grammar grammar) {
        this.grammar = grammar;
    }

    public String getDOT(DFA dfa, boolean isLexer) {
        if (dfa.s0 == null)
            return null;
        ST dot = stlib.getInstanceOf("dfa");
        dot.add("name", "DFA" + dfa.decision);
        dot.add("startState", dfa.s0.stateNumber);
        dot.add("rankdir", rankdir);
        addStopStates(dot, dfa);
        addRegularStates(dot, dfa);
        addEdges(dot, dfa, isLexer);
        String output = dot.render();
        return Utils.sortLinesInString(output);
    }

    protected String getStateLabel(DFAState s) {
        if (s == null)
            return "null";
        StringBuilder buf = new StringBuilder(250);
        buf.append('s');
        buf.append(s.stateNumber);
        if (s.isAcceptState) {
            buf.append("=>").append(s.prediction);
        }
        if (s.requiresFullContext) {
            buf.append("^");
        }
        if (grammar != null) {
            Set<Integer> alts = s.getAltSet();
            if (alts != null) {
                buf.append("\\n");
                // separate alts
                IntegerList altList = new IntegerList();
                altList.addAll(alts);
                altList.sort();
                Set<ATNConfig> configurations = s.configs;
                for (int altIndex = 0; altIndex < altList.size(); altIndex++) {
                    int alt = altList.get(altIndex);
                    if (altIndex > 0) {
                        buf.append("\\n");
                    }
                    buf.append("alt");
                    buf.append(alt);
                    buf.append(':');
                    // get a list of configs for just this alt
                    // it will help us print better later
                    List<ATNConfig> configsInAlt = new ArrayList<ATNConfig>();
                    for (ATNConfig c : configurations) {
                        if (c.alt != alt)
                            continue;
                        configsInAlt.add(c);
                    }
                    int n = 0;
                    for (int cIndex = 0; cIndex < configsInAlt.size(); cIndex++) {
                        ATNConfig c = configsInAlt.get(cIndex);
                        n++;
                        buf.append(c.toString(null, false));
                        if ((cIndex + 1) < configsInAlt.size()) {
                            buf.append(", ");
                        }
                        if (n % 5 == 0 && (configsInAlt.size() - cIndex) > 3) {
                            buf.append("\\n");
                        }
                    }
                }
            }
        }
        String stateLabel = buf.toString();
        return stateLabel;
    }

    public String getDOT(DFA dfa, boolean isLexer) {
        if (dfa.s0 == null)
            return null;
        ST dot = stlib.getInstanceOf("dfa");
        dot.add("name", "DFA" + dfa.decision);
        dot.add("startState", dfa.s0.stateNumber);
        dot.add("rankdir", rankdir);
        addStopStates(dot, dfa);
        addRegularStates(dot, dfa);
        addEdges(dot, dfa, isLexer);
        String output = dot.render();
        return Utils.sortLinesInString(output);
    }

    public String getDOT(DFA dfa, boolean isLexer) {
        if (dfa.s0 == null)
            return null;
        ST dot = stlib.getInstanceOf("dfa");
        dot.add("name", "DFA" + dfa.decision);
        dot.add("startState", dfa.s0.stateNumber);
        dot.add("rankdir", rankdir);
        addStopStates(dot, dfa);
        addRegularStates(dot, dfa);
        addEdges(dot, dfa, isLexer);
        String output = dot.render();
        return Utils.sortLinesInString(output);
    }

    public String getDOT(DFA dfa, boolean isLexer) {
        if (dfa.s0 == null)
            return null;
        ST dot = stlib.getInstanceOf("dfa");
        dot.add("name", "DFA" + dfa.decision);
        dot.add("startState", dfa.s0.stateNumber);
        dot.add("rankdir", rankdir);
        addStopStates(dot, dfa);
        addRegularStates(dot, dfa);
        addEdges(dot, dfa, isLexer);
        String output = dot.render();
        return Utils.sortLinesInString(output);
    }

    /**
     * Do a depth-first walk of the state machine graph and
     *  fill a DOT description template.  Keep filling the
     *  states and edges attributes.  We know this is an ATN
     *  for a rule so don't traverse edges to other rules and
     *  don't go past rule end state.
     */
    // protected void walkRuleATNCreatingDOT(ST dot,
    // ATNState s)
    // {
    // if ( markedStates.contains(s) ) {
    // return; // already visited this node
    // }
    // 
    // markedStates.add(s.stateNumber); // mark this node as completed.
    // 
    // // first add this node
    // ST stateST;
    // if ( s instanceof RuleStopState ) {
    // stateST = stlib.getInstanceOf("stopstate");
    // }
    // else {
    // stateST = stlib.getInstanceOf("state");
    // }
    // stateST.add("name", getStateLabel(s));
    // dot.add("states", stateST);
    // 
    // if ( s instanceof RuleStopState )  {
    // return; // don't go past end of rule node to the follow states
    // }
    // 
    // // special case: if decision point, then line up the alt start states
    // // unless it's an end of block
    // if ( s instanceof DecisionState ) {
    // GrammarAST n = ((ATNState)s).ast;
    // if ( n!=null && s instanceof BlockEndState ) {
    // ST rankST = stlib.getInstanceOf("decision-rank");
    // ATNState alt = (ATNState)s;
    // while ( alt!=null ) {
    // rankST.add("states", getStateLabel(alt));
    // if ( alt.transition(1) !=null ) {
    // alt = (ATNState)alt.transition(1).target;
    // }
    // else {
    // alt=null;
    // }
    // }
    // dot.add("decisionRanks", rankST);
    // }
    // }
    // 
    // // make a DOT edge for each transition
    // ST edgeST = null;
    // for (int i = 0; i < s.getNumberOfTransitions(); i++) {
    // Transition edge = (Transition) s.transition(i);
    // if ( edge instanceof RuleTransition ) {
    // RuleTransition rr = ((RuleTransition)edge);
    // // don't jump to other rules, but display edge to follow node
    // edgeST = stlib.getInstanceOf("edge");
    // if ( rr.rule.g != grammar ) {
    // edgeST.add("label", "<"+rr.rule.g.name+"."+rr.rule.name+">");
    // }
    // else {
    // edgeST.add("label", "<"+rr.rule.name+">");
    // }
    // edgeST.add("src", getStateLabel(s));
    // edgeST.add("target", getStateLabel(rr.followState));
    // edgeST.add("arrowhead", arrowhead);
    // dot.add("edges", edgeST);
    // walkRuleATNCreatingDOT(dot, rr.followState);
    // continue;
    // }
    // if ( edge instanceof ActionTransition ) {
    // edgeST = stlib.getInstanceOf("action-edge");
    // }
    // else if ( edge instanceof PredicateTransition ) {
    // edgeST = stlib.getInstanceOf("edge");
    // }
    // else if ( edge.isEpsilon() ) {
    // edgeST = stlib.getInstanceOf("epsilon-edge");
    // }
    // else {
    // edgeST = stlib.getInstanceOf("edge");
    // }
    // edgeST.add("label", getEdgeLabel(edge.toString(grammar)));
    // edgeST.add("src", getStateLabel(s));
    // edgeST.add("target", getStateLabel(edge.target));
    // edgeST.add("arrowhead", arrowhead);
    // dot.add("edges", edgeST);
    // walkRuleATNCreatingDOT(dot, edge.target); // keep walkin'
    // }
    // }
    /**
     * Fix edge strings so they print out in DOT properly;
     *  generate any gated predicates on edge too.
     */
    protected String getEdgeLabel(String label) {
        label = label.replace("\\", "\\\\");
        label = label.replace("\"", "\\\"");
        label = label.replace("\n", "\\\\n");
        label = label.replace("\r", "");
        return label;
    }

    protected String getStateLabel(ATNState s) {
        if (s == null)
            return "null";
        String stateLabel = "";
        if (s instanceof BlockStartState) {
            stateLabel += "&rarr;\\n";
        } else if (s instanceof BlockEndState) {
            stateLabel += "&larr;\\n";
        }
        stateLabel += String.valueOf(s.stateNumber);
        if (s instanceof PlusBlockStartState || s instanceof PlusLoopbackState) {
            stateLabel += "+";
        } else if (s instanceof StarBlockStartState || s instanceof StarLoopEntryState || s instanceof StarLoopbackState) {
            stateLabel += "*";
        }
        if (s instanceof DecisionState && ((DecisionState) s).decision >= 0) {
            stateLabel = stateLabel + "\\nd=" + ((DecisionState) s).decision;
        }
        return stateLabel;
    }

    private void addStopStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (!d.isAcceptState)
                continue;
            ST st = stlib.getInstanceOf("stopstate");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addRegularStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.isAcceptState || d.stateNumber == Integer.MAX_VALUE)
                continue;
            ST st = stlib.getInstanceOf("state");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addEdges(ST dot, DFA dfa, boolean isLexer) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.edges != null) {
                for (int i = 0; i < d.edges.length; i++) {
                    DFAState target = d.edges[i];
                    if (target == null || target.stateNumber == Integer.MAX_VALUE)
                        continue;
                    // we shift up for EOF as -1 for parser
                    int ttype = i - 1;
                    String label = isLexer ? "\'" + getEdgeLabel(String.valueOf((char) i)) + "\'" : (grammar != null ? grammar.getTokenDisplayName(ttype) : String.valueOf(ttype));
                    ST st = stlib.getInstanceOf("edge");
                    st.add("label", label);
                    st.add("src", "s" + d.stateNumber);
                    st.add("target", "s" + target.stateNumber);
                    st.add("arrowhead", arrowhead);
                    dot.add("edges", st);
                }
            }
        }
    }

    private void addStopStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (!d.isAcceptState)
                continue;
            ST st = stlib.getInstanceOf("stopstate");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addRegularStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.isAcceptState || d.stateNumber == Integer.MAX_VALUE)
                continue;
            ST st = stlib.getInstanceOf("state");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addEdges(ST dot, DFA dfa, boolean isLexer) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.edges != null) {
                for (int i = 0; i < d.edges.length; i++) {
                    DFAState target = d.edges[i];
                    if (target == null || target.stateNumber == Integer.MAX_VALUE)
                        continue;
                    // we shift up for EOF as -1 for parser
                    int ttype = i - 1;
                    String label = isLexer ? "\'" + getEdgeLabel(String.valueOf((char) i)) + "\'" : (grammar != null ? grammar.getTokenDisplayName(ttype) : String.valueOf(ttype));
                    ST st = stlib.getInstanceOf("edge");
                    st.add("label", label);
                    st.add("src", "s" + d.stateNumber);
                    st.add("target", "s" + target.stateNumber);
                    st.add("arrowhead", arrowhead);
                    dot.add("edges", st);
                }
            }
        }
    }

    private void addStopStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (!d.isAcceptState)
                continue;
            ST st = stlib.getInstanceOf("stopstate");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addRegularStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.isAcceptState || d.stateNumber == Integer.MAX_VALUE)
                continue;
            ST st = stlib.getInstanceOf("state");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addEdges(ST dot, DFA dfa, boolean isLexer) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.edges != null) {
                for (int i = 0; i < d.edges.length; i++) {
                    DFAState target = d.edges[i];
                    if (target == null || target.stateNumber == Integer.MAX_VALUE)
                        continue;
                    // we shift up for EOF as -1 for parser
                    int ttype = i - 1;
                    String label = isLexer ? "\'" + getEdgeLabel(String.valueOf((char) i)) + "\'" : (grammar != null ? grammar.getTokenDisplayName(ttype) : String.valueOf(ttype));
                    ST st = stlib.getInstanceOf("edge");
                    st.add("label", label);
                    st.add("src", "s" + d.stateNumber);
                    st.add("target", "s" + target.stateNumber);
                    st.add("arrowhead", arrowhead);
                    dot.add("edges", st);
                }
            }
        }
    }

    private void addStopStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (!d.isAcceptState)
                continue;
            ST st = stlib.getInstanceOf("stopstate");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addRegularStates(ST dot, DFA dfa) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.isAcceptState || d.stateNumber == Integer.MAX_VALUE)
                continue;
            ST st = stlib.getInstanceOf("state");
            st.add("name", "s" + d.stateNumber);
            st.add("label", getStateLabel(d));
            dot.add("states", st);
        }
    }

    private void addEdges(ST dot, DFA dfa, boolean isLexer) {
        for (DFAState d : dfa.states.keySet()) {
            if (d.edges != null) {
                for (int i = 0; i < d.edges.length; i++) {
                    DFAState target = d.edges[i];
                    if (target == null || target.stateNumber == Integer.MAX_VALUE)
                        continue;
                    // we shift up for EOF as -1 for parser
                    int ttype = i - 1;
                    String label = isLexer ? "\'" + getEdgeLabel(String.valueOf((char) i)) + "\'" : (grammar != null ? grammar.getTokenDisplayName(ttype) : String.valueOf(ttype));
                    ST st = stlib.getInstanceOf("edge");
                    st.add("label", label);
                    st.add("src", "s" + d.stateNumber);
                    st.add("target", "s" + target.stateNumber);
                    st.add("arrowhead", arrowhead);
                    dot.add("edges", st);
                }
            }
        }
    }
}
