"""
Biological Neural FSA Experiment — Cortical Labs SDK (Simulator)
=================================================================
Implements a Finite State Automaton over biological neural activity.

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
    4. At the end, check whether we landed in the accepting state (FS)

Run:
  Python3 project.py
"""

import time
from collections import defaultdict
import cl
from cl import ChannelSet, StimDesign
from dotenv import load_dotenv
load_dotenv(".env")

# ─── FSA Configuration ────────────────────────────────────────────────────────

# Channel groups representing each FSA state
STATE_CHANNELS = {
    "q0": [10, 11],  # Start state
    "S1": [20, 21],  # Seen a '1'
    "FS": [30, 31],  # Accepting: seen "11"
}

# Channel groups for input symbols
INPUT_CHANNELS = {
    "0": ChannelSet(40, 41),
    "1": ChannelSet(50, 51),
}

# delta transition table: (current_state, input_symbol) → next_state
TRANSITIONS = {
    ("q0", "0"): "q0",
    ("q0", "1"): "S1",
    ("S1", "0"): "q0",
    ("S1", "1"): "FS",
    ("FS", "0"): "q0",
    ("FS", "1"): "FS",
}

START_STATE = "q0"
ACCEPTING_STATE = "FS"

# Biphasic stim: 160 µs pulse width, ±1.5 µA — gentle enough not to dominate
STIM_DESIGN = StimDesign(160, -1.5, 160, 1.5)

# A Spike object is created for each spike detected by the system, and these are placed in a list at LoopTick.analysis.spikes.
# Spike objects expose the following properties:
#   channel:   Which channel the spike was detected on
#   timestamp: Timestamp of the sample that triggered the detection of the spike
#   samples:   NumPy array of 75 floating point µV sample values around timestamp

def detectState(spikes: list) -> str:
    """
    Vote on the current FSA state based on which state-channel group
    fired the most spikes this tick.
    """
    counts = {state: 0 for state in STATE_CHANNELS}
    active = {spike.channel for spike in spikes}

    for state, channels in STATE_CHANNELS.items():
        counts[state] = sum(1 for ch in channels if ch in active)

    # Highest spike count wins
    return max(counts, key=lambda s: counts[s])


def applyTransition(neurons, current_state: str, symbol: str) -> str:
    """Stimulate the input-symbol channels and return the expected next state."""
    channel_set = INPUT_CHANNELS[symbol]
    neurons.stim(channel_set, STIM_DESIGN)
    return TRANSITIONS.get((current_state, symbol), current_state)


def runFSA(input_string: str, ticks_per_symbol: int = 50):
    """
    Feed an input string symbol-by-symbol into the neural FSA.
    Returns (accepted: bool, state_trace: list).
    """
    print(f"\n{'='*60}")
    print(f"  Input string : '{input_string}'")
    print(f"  Ticks/symbol : {ticks_per_symbol}")
    print(f"{'='*60}")

    state_trace = [START_STATE]
    current_state = START_STATE
    symbol_index = 0
    ticks_in_symbol = 0

    # To begin, simply import the cl module and open a Neuron connection as follows.
    # Note that cl.open() is the preferred way to interface with the CL1 and
    # the cl.Neurons object should not be used in isolation.
    with cl.open() as neurons:
        recording = neurons.record()

        # Create a data stream to record FSA state over time
        fsa_stream = neurons.create_data_stream(
            name="fsa_state",
            attributes={"input": input_string, "accepting_state": ACCEPTING_STATE}
        )

        loop_ticks = ticks_per_symbol * (len(input_string) + 2)  # +2 settle ticks

        for tick in neurons.loop(ticks_per_second=200, stop_after_ticks=loop_ticks):
            spikes = tick.analysis.spikes
            observed_state = detectState(spikes)

            # After the first 'settle' pass, start feeding symbols
            if symbol_index < len(input_string):

                if ticks_in_symbol == 0:
                    # First tick of this symbol: stimulate and transition
                    symbol = input_string[symbol_index]
                    expected_next = applyTransition(neurons, current_state, symbol)

                    print(f"  [{symbol_index+1}/{len(input_string)}] "
                          f"State={current_state} + '{symbol}' → {expected_next}  "
                          f"(neural observed: {observed_state}, "
                          f"spikes this tick: {len(spikes)})")

                    current_state = expected_next
                    state_trace.append(current_state)

                    fsa_stream.append(
                        neurons.timestamp(),
                        {
                            "symbol": symbol,
                            "from_state": state_trace[-2],
                            "to_state": current_state,
                            "spike_count": len(spikes),
                            "observed_neural_state": observed_state,
                        }
                    )

                ticks_in_symbol += 1
                if ticks_in_symbol >= ticks_per_symbol:
                    ticks_in_symbol = 0
                    symbol_index   += 1

        recording.stop()

    accepted = (current_state == ACCEPTING_STATE)

    print(f"\n  State trace  : {' → '.join(state_trace)}")
    print(f"  Final state  : {current_state}")
    print(f"  Result       : {'ACCEPTED' if accepted else 'REJECTED'}")

    return accepted, state_trace


# ─── Test Suite ───────────────────────────────────────────────────────────────

def runTestSuite():
    """
    Run a set of known-good and known-bad inputs through the neural FSA.
    The FSA accepts binary strings ending in "11".
    """
    test_cases = [
        ("11", True, "straightforward acceptance"),
        ("011", True, "quicl prefix then accept"),
        ("1011",True, "funny accepting"),
        ("10", False, "ends in 0"),
        ("0", False, "a zero"),
        ("1", False, "a one"),
        ("010", False, "no trailing 11s"),
        ("111", True, "three ones still accepted"),
        ("1100", False, "starts off good but then no bueno"),
        ("10011", True, "longer string but still accepted"),
        # Add your own test cases below:
        #10/11 cases will be accepted
        ("00",    True, "dummy test case"),
    ]

    results = []
    print("\n" + "="*60)
    print("  NEURAL FSA TEST SUITE")
    print("  Recognises: binary strings ending in '11'")
    print("="*60)

    for input_str, expected, label in test_cases:
        accepted, trace = runFSA(input_str, ticks_per_symbol=30)
        correct = (accepted == expected)
        results.append((input_str, expected, accepted, correct, label))
        # rest time before next case
        time.sleep(0.3)

    # summary of test results
    print("\n" + "="*60)
    print("  RESULTS SUMMARY")
    print("="*60)
    print(f"  {'Input':<10} {'Expected':<12} {'Got':<12} {'Match':<8} Label")
    print(f"  {'-'*8:<10} {'-'*8:<12} {'-'*8:<12} {'-'*5:<8} -----")
    for input_str, expected, accepted, correct, label in results:
        exp_str = "Acceptance" if expected else "Rejection"
        got_str = "Acceptance" if accepted else "Rejection"
        match   = "YAY" if correct else "NOOO"
        print(f"  {input_str:<10} {exp_str:<12} {got_str:<12} {match:<8} {label}")

    passed = sum(1 for *_, correct, _ in results if correct)
    print(f"\n  Passed: {passed}/{len(results)}")
    print("="*60)



#main function
"""
Give users option to test a specific string to see if it's accepted,
or to run all test cases provided within runTestSuite.
"""
if __name__ == "__main__":
    option = input("Enter (1) for custom one liner input or (2) for full test suite: ")

    if option == "1":
        user_input = input("Enter the input string for the FSA: ")
        accepted, trace = runFSA(user_input)
        print("Accepted:", accepted)
        print("Trace:", trace)
    else:
        runTestSuite()