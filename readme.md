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

==============================================================================================
Implements a Finite State Automaton (FSA) over biological neural activity.

FSA Definition (recognises binary strings ending in "11"):
  States: q0 (start), S1 (seen one '1'), FS (accepting — seen "11")

Channel Mapping:
  Start State  → channels 10, 11   (start state, q0)
  S1  → channels 20, 21   (intermediate state)
  FS  → channels 30, 31   (Final State, FS)

Input Symbols:
  '0' → stimulate channels 40, 41
  '1' → stimulate channels 50, 51

Transition Logic:
  Each tick we:
    1. Count spikes/state-channel group → thus we can determine current state we are in
    2. Apply next input symbol via stimulation(essentially the delta transition)
    3. Record the transition
    4. At the end, determine whether we landed in the accepting state (FS) or not


Extra libraries and why:


from dotenv import load_dotenv
load_dotenv(".env")


To run:
  Python3 project.py
"""

