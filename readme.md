"""
Biological Neural FSA Experiment — Cortical Labs SDK (Simulator)

@CITATION:
@software{cl_api_2026,
    author  = {
                David Hogan and Andrew Doherty and Boon Kien Khoo and
                Johnson Zhou and Richard Salib and James Stewart and
                Kiaran Lawson and Alon Loeffler and Brett J. Kagan
              },
    title   = {CL API: Real-Time Closed-Loop Interactions with Biological Neural Networks},
    version = {1.0},
    doi     = {10.48550/arXiv.2602.11632},
    year    = {2026}
}

For installation: https://docs.corticallabs.com/#installation

CL API Documentation Pre-Release: https://github.com/Cortical-Labs/cl-api-doc/tree/main

=================================================================
Implements a Finite State Automaton (FSA) over biological neural activity.

FSA Definition (recognises binary strings ending in "11"):
  States: S0 (start), S1 (seen one '1'), S2 (accepting — seen "11")

Channel Mapping:
  S0  → channels 10, 11   (start state)
  S1  → channels 20, 21   (intermediate state)
  S2  → channels 30, 31   (ACCEPTING state)

Input Symbols:
  '0' → stimulate channels 40, 41
  '1' → stimulate channels 50, 51

Transition Logic (closed-loop):
  Each tick we:
    1. Count spikes per state-channel group → determine current state
    2. Apply next input symbol via stimulation
    3. Record the transition
    4. At the end, check whether we landed in the accepting state (S2)

To run:
  Python3 project.py
"""

