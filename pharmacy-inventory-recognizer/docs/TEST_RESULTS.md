# Test Cases and Results

All results below were produced by running the simulator (`python cli/simulator.py --demo`) and the test suite (`cd backend && pytest -v`). Re-run them before the defense and replace this file if anything changes.

## 1. Accepted set (10 cases)

| # | Input | State path | Final state | Expected | Actual | Pass | Reason |
|---|---|---|---|---|---|---|---|
| 1 | `M001` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Medicine code |
| 2 | `M123` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Medicine code |
| 3 | `S001` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Supplement code |
| 4 | `S002` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Supplement code |
| 5 | `C001` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Consumable code |
| 6 | `C002` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Consumable code |
| 7 | `M999` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Medicine code |
| 8 | `S250` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Supplement code |
| 9 | `C500` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Consumable code |
| 10 | `M042` | q0 → q1 → q2 → q3 → q4 | q4 | ACCEPTED | ACCEPTED | ✅ | valid Medicine code |

## 2. Rejected set (10 cases)

| # | Input | State path | Final state | Expected | Actual | Pass | Reason |
|---|---|---|---|---|---|---|---|
| 11 | `M01` | q0 → q1 → q2 → q3 | q3 | REJECTED | REJECTED | ✅ | too short (3 symbols) - expected exactly 4 |
| 12 | `C0012` | q0 → q1 → q2 → q3 → q4 → qDead | qDead | REJECTED | REJECTED | ✅ | too long (5 symbols) - expected exactly 4 |
| 13 | `A123` | q0 → qDead → qDead → qDead → qDead | qDead | REJECTED | REJECTED | ✅ | contains symbol(s) not in the alphabet: 'A' |
| 14 | `123` | q0 → qDead → qDead → qDead | qDead | REJECTED | REJECTED | ✅ | first symbol must be a category letter (M, S or C) |
| 15 | `MM123` | q0 → q1 → qDead → qDead → qDead → qDead | qDead | REJECTED | REJECTED | ✅ | symbol 2 must be a digit, found 'M' |
| 16 | `C12A` | q0 → q1 → q2 → q3 → qDead | qDead | REJECTED | REJECTED | ✅ | contains symbol(s) not in the alphabet: 'A' |
| 17 | ε (empty) | q0 | q0 | REJECTED | REJECTED | ✅ | empty input - a code must be a letter followed by 3 digits |
| 18 | `m123` | q0 → qDead → qDead → qDead → qDead | qDead | REJECTED | REJECTED | ✅ | contains symbol(s) not in the alphabet: 'm' |
| 19 | `S12` | q0 → q1 → q2 → q3 | q3 | REJECTED | REJECTED | ✅ | too short (3 symbols) - expected exactly 4 |
| 20 | `S1234` | q0 → q1 → q2 → q3 → q4 → qDead | qDead | REJECTED | REJECTED | ✅ | too long (5 symbols) - expected exactly 4 |

## 3. Edge cases

| # | Input | Tests | State path | Final state | Actual | Pass |
|---|---|---|---|---|---|---|
| 21 | `M 12` | space is not in Σ | q0 → q1 → qDead → qDead → qDead | qDead | REJECTED | ✅ |
| 22 | `0M12` | digit before letter | q0 → qDead → qDead → qDead → qDead | qDead | REJECTED | ✅ |
| 23 | `MS12` | two letters | q0 → q1 → qDead → qDead → qDead | qDead | REJECTED | ✅ |
| 24 | `C1S2` | letter in a digit position | q0 → q1 → q2 → qDead → qDead | qDead | REJECTED | ✅ |
| 25 | `M00` | 3 symbols, one digit short | q0 → q1 → q2 → q3 | q3 | REJECTED | ✅ |

## 4. Automated tests

```
tests/test_equivalence.py::test_minimized_dfa_is_rebuilt_from_nfa PASSED [  8%]
tests/test_equivalence.py::test_state_counts PASSED                      [ 16%]
tests/test_equivalence.py::test_re_nfa_dfa_mindfa_agree_on_every_string PASSED [ 25%]
tests/test_equivalence.py::test_theory_report_for_web_page PASSED        [ 33%]
tests/test_equivalence.py::test_language_size_is_3000 PASSED             [ 41%]
tests/test_recognizer.py::test_all_accepted_strings_are_accepted PASSED  [ 50%]
tests/test_recognizer.py::test_all_rejected_strings_are_rejected PASSED  [ 58%]
tests/test_recognizer.py::test_symbols_outside_alphabet_are_flagged PASSED [ 66%]
tests/test_recognizer.py::test_wrong_length_is_rejected PASSED           [ 75%]
tests/test_recognizer.py::test_trace_length_matches_input_length PASSED  [ 83%]
tests/test_recognizer.py::test_recognizer_decodes_valid_codes PASSED     [ 91%]
tests/test_recognizer.py::test_recognizer_gives_a_reason_when_rejecting PASSED [100%]
============================== 12 passed in 0.28s ==============================
```

`test_equivalence.py` checks the regular expression, NFA, subset DFA and minimized DFA against each other on more than 30,000 strings, and checks the data shown on the web app's Automata Theory page.

## 5. Summary

All 25 simulator cases and all automated tests pass. Every expected-accepted code ends in the accepting state q4, and every expected-rejected code ends in a non-accepting state: q0 (empty input), q3 (one digit short) or qDead (anything else).
