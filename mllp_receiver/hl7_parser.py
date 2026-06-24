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
            # Skip batch wrapper segments
            continue

        if segment.startswith("MSH|"):
            # Save previous message if one was being built
            if current_message:
                messages.append("\r".join(current_message))
            current_message = [segment]
        else:
            if current_message:
                current_message.append(segment)

    # Don't forget the last message
    if current_message:
        messages.append("\r".join(current_message))

    logger.info(f"Split batch into {len(messages)} individual message(s)")
    return messages


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