# hl7-mllp-receiver
Python-based MLLP receiver for HL7 v2.x messages over TCP/IP
Open README.md, delete everything, and paste this:
markdown# HL7 v2.x MLLP Receiver

A Python-based MLLP receiver that accepts HL7 v2.x messages over TCP/IP, parses
them, and returns HL7 ACK responses. Built as a healthcare integration learning
project covering TCP socket programming, MLLP framing, HL7 message structure,
and HL7 parsing libraries.

## Features

- Listens on multiple configured TCP ports simultaneously (multi-threaded)
- Receives MLLP-framed HL7 messages
- Supports both single HL7 messages and batch HL7 messages (FHS/BHS/BTS/FTS)
- Generates HL7 ACK responses (AA, AE, AR) for every processed message
- Parses HL7 using the `hl7apy` library (selected after evaluating `hl7apy` vs `python-hl7`)
- Handles malformed messages, bad connections, and port failures without crashing
- Structured logging of all operational events and exceptions
- Reads listener configuration from an external JSON file

## Project Structure
hl7-mllp-receiver/

mllp_receiver/

main.py             Entry point — loads config, starts all listeners

config_loader.py    Loads and validates JSON listener configuration

listener.py         TCP server, client handling, message routing

mllp.py             MLLP framing — wrap/extract HL7 payloads

hl7_parser.py        Manual parsing + hl7apy-based parsing, batch splitting

ack_builder.py      Builds AA/AE/AR HL7 ACK messages

logger_config.py    Logging setup

data/

sample_single_message.hl7

sample_batch_message.hl7

docs/

library_comparison.py

library_comparison_notes.md

tests/

test_mllp.py

test_hl7_parser.py

test_ack_builder.py

test_config_loader.py

config.json

test_client.py

requirements.txt

## Setup

```bash
git clone https://github.com/kulkarnisankalp598-png/hl7-mllp-receiver.git
cd hl7-mllp-receiver
py -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### Dependencies
- Python 3.11+
- `hl7apy` — HL7 message parsing
- `pytest` — unit testing

## Configuration

Listener ports are configured in `config.json`:

```json
{
  "application": {
    "name": "Python HL7 MLLP Receiver",
    "logLevel": "INFO"
  },
  "listeners": [
    {
      "name": "ADTListener",
      "ipAddress": "0.0.0.0",
      "port": 2575,
      "receiveTimeoutSeconds": 30,
      "maxMessageSizeKb": 1024,
      "ackMode": "MESSAGE_LEVEL"
    },
    {
      "name": "LabListener",
      "ipAddress": "0.0.0.0",
      "port": 2576,
      "receiveTimeoutSeconds": 30,
      "maxMessageSizeKb": 2048,
      "ackMode": "MESSAGE_LEVEL"
    }
  ]
}
```

Each listener starts on its own thread. If one listener fails to bind (e.g. port
already in use), the others continue running.

## Running the Receiver

```bash
py -m mllp_receiver.main
```

The receiver will load `config.json`, start a listener thread per configured
port, and wait for incoming connections. Press `Ctrl+C` to stop.

## Testing with the Test Client

With the receiver running in one terminal, open a second terminal and run:

```bash
py test_client.py
```

This sends a single HL7 message and a batch HL7 message to the receiver over
TCP using MLLP framing, and prints the ACK response(s) received back.

Example output:
=== SINGLE MESSAGE TEST ===

Connected to 127.0.0.1:2575

Sent message (158 chars)

Received ACK 1/1:

MSH|^~&|ReceiverApp|...||ACK|ACKMSG00001|P|2.5

MSA|AA|MSG00001

## HL7 Parsing: Manual vs Library-Based

As a learning exercise, `hl7_parser.py` includes a manual parsing function
(`extract_basic_fields`) that splits the raw message string by segment and
field delimiters to extract MSH-9 (message type) and MSH-10 (control ID).

The final, production-style implementation uses the `hl7apy` library
(`parse_with_hl7apy`) for all message parsing in the live receiver
(`listener.py`). See `docs/library_comparison_notes.md` for the full evaluation
of `hl7apy` vs `python-hl7` and the reasoning behind selecting `hl7apy`.

## MLLP Framing

HL7 messages are wrapped in MLLP framing before being sent over TCP:
<VT>HL7_MESSAGE<FS><CR>

| Character | Hex | Meaning |
|---|---|---|
| VT | 0x0B | Start of message |
| FS | 0x1C | End of message |
| CR | 0x0D | Final carriage return |

`mllp.py` handles wrapping outgoing messages and extracting incoming payloads,
including detection of malformed frames (missing start or end blocks).

## Batch Message Handling

Batch HL7 files contain an `FHS` (file header), `BHS` (batch header), one or
more `MSH`-based messages, a `BTS` (batch trailer), and an `FTS` (file
trailer). The receiver detects batch messages by checking for `FHS`/`BHS` at
the start, splits the batch into individual MSH-based messages, processes and
parses each one independently with `hl7apy`, and sends a separate ACK for each
message. If one message in a batch fails to parse, the failure is logged and
the receiver continues processing the remaining messages.

## ACK Generation

| Code | Meaning |
|---|---|
| AA | Application Accept — message processed successfully |
| AE | Application Error — error while processing |
| AR | Application Reject — message rejected (e.g. failed to parse) |

Every ACK includes the original message's MSH-10 control ID in the MSA
segment, and is wrapped in MLLP framing before being sent back over the same
TCP connection.

## Exception Handling

- Malformed MLLP frames are logged and the connection continues listening for the next message.
- Parsing failures generate an AR or AE ACK instead of crashing.
- Client disconnects are caught and logged; the listener continues accepting new connections.
- A failure to bind one listener port does not prevent other configured listeners from starting.
- Unexpected exceptions are logged with full stack traces.

## Logging

The application logs:
- Startup and configuration loading
- Listener startup success/failure per port
- Client connect/disconnect events
- Message metadata (type, control ID) — not full patient payloads
- ACKs sent
- All exceptions, including stack traces for unexpected errors

Full patient message content is not logged by default to avoid unnecessary
exposure of PHI-style data, even though this project uses synthetic sample
data only.

## Running Tests

```bash
py -m pytest tests/ -v
```

49 tests covering:
- MLLP wrapping/extraction and malformed frame handling
- Manual and hl7apy-based HL7 parsing (single and batch)
- ACK generation for AA, AE, and AR codes
- Configuration loading and listener validation

## Sample Data

- `data/sample_single_message.hl7` — a single ADT^A01 message
- `data/sample_batch_message.hl7` — a batch containing two ADT^A01 messages with FHS/BHS/BTS/FTS wrappers

All sample data uses synthetic patient identifiers. No real PHI is used
anywhere in this project.

## Library Selection

After evaluating both `hl7apy` and `python-hl7` (see
`docs/library_comparison_notes.md`), **hl7apy** was selected as the parsing
library for the final implementation due to its readable attribute-based
field access, built-in validation levels, and richer object model that
closely mirrors the HL7 segment/field/component structure.

## Known Limitations

- This is a learning-oriented implementation, not a production healthcare integration engine.
- No TLS/encryption — all communication is plain TCP.
- No persistence layer — messages are not stored after ACK is sent.
- No IP allowlist or authentication on incoming connections.
- ACK mode configuration (`MESSAGE_LEVEL`) is read but not yet used to vary ACK behavior — all responses default to message-level ACKs.