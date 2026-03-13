# Biological-Neural-Finite-State-Automata# Biological-Neural-Finite-State-Automata

## Biological Neural FSA Experiment — Cortical Labs SDK (Simulator)
=================================================================
Implements a Finite State Automaton (FSA) over biological neural activity.

FSA Definition (recognises binary strings ending in "11"):
  States: Start State (q0), S1 (seen a '1'), FS (accepting — seen "11")

Channel Mapping:
  q0  → channels 10, 11   (start state)
  S1  → channels 20, 21   (intermediate state)
  FS  → channels 30, 31   (final state)

Input Symbols:
  '0' → stimulate channels 40, 41
  '1' → stimulate channels 50, 51

Transition Logic (closed-loop):
  Each tick we:
    1. Count spikes per state-channel group → determine current state
    2. Apply next input symbol via stimulation
    3. Record the transition
    4. At the end, check whether we landed in the accepting state (FS) or not