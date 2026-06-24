# HL7 Library Comparison: hl7apy vs python-hl7

## Summary
Both libraries were installed and tested against the same sample HL7 ADT^A01 message
and an invalid message missing the MSH segment.

## Test Results

| Area | hl7apy | python-hl7 |
|---|---|---|
| Installation | `pip install hl7apy` — no dependencies | `pip install hl7` — no dependencies |
| Parsing syntax | Attribute access: `msg.msh.message_type.value` | Index access: `msg.segment('MSH')[9]` |
| Ease of use | More verbose but self-documenting | Shorter syntax, requires knowing field positions |
| Validation support | Built-in validation levels (strict/tolerant) | No built-in validation, relies on try/except |
| Error messages | Generic ("Invalid message") | More specific ("First segment is PID, must be MSH/FHS/BHS") |
| Documentation | Full docs at hl7apy.readthedocs.io with examples | Shorter README on GitHub, fewer examples |
| Batch support | No native batch helper found in basic testing | No native batch helper found in basic testing |
| ACK support | No built-in ACK builder | No built-in ACK builder |
| Object model | Rich object model (segments, fields, components) | Simpler list-based segment access |

## Decision: Selected Library — hl7apy

**Reasoning:**
1. hl7apy's attribute-based access (`msg.msh.message_type.value`) is more readable and
   self-documenting than index-based access, which makes the code easier to maintain
   and review.
2. hl7apy has built-in validation levels which give more control over how strict
   parsing should be — useful for catching malformed messages early.
3. hl7apy's object model maps more directly to the HL7 segment/field/component
   structure described in the official spec, which made it easier to understand
   while learning HL7 for the first time.
4. hl7apy has more thorough official documentation with working examples.

**Tradeoff noted:** python-hl7's error messages were actually more specific and
helpful during testing. If error message clarity becomes a blocker, this could be
revisited, but for the scope of this project hl7apy's structure and validation
outweigh that difference.

## Test Evidence
Both libraries correctly:
- Parsed MSH-9 (message type: ADT^A01) and MSH-10 (control ID: MSG00001) from a valid message
- Raised an exception when given an invalid message missing the MSH segment

See `docs/library_comparison.py` for the test script used to generate these results.# HL7 Library Comparison: hl7apy vs python-hl7

## Summary
Both libraries were installed and tested against the same sample HL7 ADT^A01 message
and an invalid message missing the MSH segment.

## Test Results

| Area | hl7apy | python-hl7 |
|---|---|---|
| Installation | `pip install hl7apy` — no dependencies | `pip install hl7` — no dependencies |
| Parsing syntax | Attribute access: `msg.msh.message_type.value` | Index access: `msg.segment('MSH')[9]` |
| Ease of use | More verbose but self-documenting | Shorter syntax, requires knowing field positions |
| Validation support | Built-in validation levels (strict/tolerant) | No built-in validation, relies on try/except |
| Error messages | Generic ("Invalid message") | More specific ("First segment is PID, must be MSH/FHS/BHS") |
| Documentation | Full docs at hl7apy.readthedocs.io with examples | Shorter README on GitHub, fewer examples |
| Batch support | No native batch helper found in basic testing | No native batch helper found in basic testing |
| ACK support | No built-in ACK builder | No built-in ACK builder |
| Object model | Rich object model (segments, fields, components) | Simpler list-based segment access |

## Decision: Selected Library — hl7apy

**Reasoning:**
1. hl7apy's attribute-based access (`msg.msh.message_type.value`) is more readable and
   self-documenting than index-based access, which makes the code easier to maintain
   and review.
2. hl7apy has built-in validation levels which give more control over how strict
   parsing should be — useful for catching malformed messages early.
3. hl7apy's object model maps more directly to the HL7 segment/field/component
   structure described in the official spec, which made it easier to understand
   while learning HL7 for the first time.
4. hl7apy has more thorough official documentation with working examples.

**Tradeoff noted:** python-hl7's error messages were actually more specific and
helpful during testing. If error message clarity becomes a blocker, this could be
revisited, but for the scope of this project hl7apy's structure and validation
outweigh that difference.

## Test Evidence
Both libraries correctly:
- Parsed MSH-9 (message type: ADT^A01) and MSH-10 (control ID: MSG00001) from a valid message
- Raised an exception when given an invalid message missing the MSH segment

See `docs/library_comparison.py` for the test script used to generate these results.