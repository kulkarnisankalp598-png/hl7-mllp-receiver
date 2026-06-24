import logging

logger = logging.getLogger("mllp_receiver")


def extract_basic_fields(message: str):
    """
    Manual parsing exercise — extract MSH-9 (message type) and MSH-10 (control ID)
    by splitting the message into segments and fields.
    """
    segments = message.strip().split("\r")
    msh = next((s for s in segments if s.startswith("MSH|")), None)

    if not msh:
        logger.error("Missing MSH segment in message")
        raise ValueError("Missing MSH segment")

    fields = msh.split("|")
    message_type = fields[8] if len(fields) > 8 else None
    control_id = fields[9] if len(fields) > 9 else None

    logger.info(f"Manually parsed — message_type: {message_type}, control_id: {control_id}")
    return message_type, control_id


def is_batch_message(message: str) -> bool:
    """Detect whether a message is a batch (contains FHS or BHS) vs single (starts with MSH)."""
    stripped = message.strip()
    return stripped.startswith("FHS|") or stripped.startswith("BHS|")


def split_batch_messages(batch_text: str):
    """
    Split a batch HL7 message into individual MSH-based messages.
    Skips FHS, BHS, BTS, FTS wrapper segments.
    """
    segments = [s for s in batch_text.strip().split("\r") if s.strip()]

    messages = []
    current_message = []

    for segment in segments:
        if segment.startswith(("FHS|", "BHS|", "BTS|", "FTS|")):
            continue

        if segment.startswith("MSH|"):
            if current_message:
                messages.append("\r".join(current_message))
            current_message = [segment]
        else:
            if current_message:
                current_message.append(segment)

    if current_message:
        messages.append("\r".join(current_message))

    logger.info(f"Split batch into {len(messages)} individual message(s)")
    return messages


# --- Library-based parsing using hl7apy (final implementation) ---

from hl7apy.parser import parse_message
from hl7apy.exceptions import HL7apyException


def parse_with_hl7apy(message: str):
    """
    Parse an HL7 message using the hl7apy library.
    Returns a tuple of (message_type, control_id, parsed_message_object).
    Raises ValueError on parsing failure.
    """
    try:
        msg = parse_message(message, validation_level=2)
        message_type = msg.msh.message_type.value
        control_id = msg.msh.message_control_id.value
        logger.info(f"hl7apy parsed — message_type: {message_type}, control_id: {control_id}")
        return message_type, control_id, msg
    except HL7apyException as e:
        logger.error(f"hl7apy failed to parse message: {e}")
        raise ValueError(f"hl7apy parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing message with hl7apy: {e}")
        raise ValueError(f"Unexpected parsing error: {e}")


def split_batch_messages_hl7apy(batch_text: str):
    """
    Split a batch into individual MSH-based message strings (same logic as manual
    split, since hl7apy doesn't provide a native batch splitter), then validate
    each with hl7apy.
    """
    individual_messages = split_batch_messages(batch_text)
    validated_messages = []

    for msg_text in individual_messages:
        try:
            message_type, control_id, parsed = parse_with_hl7apy(msg_text)
            validated_messages.append({
                'text': msg_text,
                'message_type': message_type,
                'control_id': control_id,
                'parsed': parsed,
                'valid': True
            })
        except ValueError as e:
            logger.error(f"Failed to validate batch message with hl7apy: {e}")
            validated_messages.append({
                'text': msg_text,
                'message_type': None,
                'control_id': None,
                'parsed': None,
                'valid': False,
                'error': str(e)
            })

    return validated_messages


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test single message parsing
    sample_single = "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|20260605120000||ADT^A01|MSG00001|P|2.5\rEVN|A01|20260605120000\rPID|1||123456^^^MRN||DOE^JOHN"

    print("--- Single message test ---")
    msg_type, control_id = extract_basic_fields(sample_single)
    print(f"Message type: {msg_type}")
    print(f"Control ID: {control_id}")
    print(f"Is batch: {is_batch_message(sample_single)}")

    # Test batch message
    sample_batch = (
        "FHS|^~\\&|SendingApp|SendingFacility\r"
        "BHS|^~\\&|SendingApp|SendingFacility\r"
        "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|20260605120000||ADT^A01|MSG00001|P|2.5\r"
        "EVN|A01|20260605120000\r"
        "PID|1||123456^^^MRN||DOE^JOHN\r"
        "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|20260605120001||ADT^A01|MSG00002|P|2.5\r"
        "EVN|A01|20260605120001\r"
        "PID|1||789012^^^MRN||SMITH^JANE\r"
        "BTS|2\r"
        "FTS|1"
    )

    print("\n--- Batch message test ---")
    print(f"Is batch: {is_batch_message(sample_batch)}")
    individual_messages = split_batch_messages(sample_batch)
    for i, msg in enumerate(individual_messages, 1):
        print(f"\nMessage {i}:")
        msg_type, control_id = extract_basic_fields(msg)
        print(f"  Type: {msg_type}, Control ID: {control_id}")

    # Test invalid message (no MSH)
    print("\n--- Invalid message test (no MSH) ---")
    try:
        extract_basic_fields("PID|1||123456^^^MRN||DOE^JOHN")
    except ValueError as e:
        print(f"Correctly caught error: {e}")

    # Test library-based parsing (hl7apy)
    print("\n--- hl7apy single message test ---")
    message_type, control_id, parsed = parse_with_hl7apy(sample_single)
    print(f"Type: {message_type}, Control ID: {control_id}")

    print("\n--- hl7apy batch message test ---")
    results = split_batch_messages_hl7apy(sample_batch)
    for i, r in enumerate(results, 1):
        print(f"Message {i}: valid={r['valid']}, type={r['message_type']}, control_id={r['control_id']}")

    print("\n--- hl7apy invalid message test ---")
    try:
        parse_with_hl7apy("PID|1||123456^^^MRN||DOE^JOHN")
    except ValueError as e:
        print(f"Correctly caught error: {e}")