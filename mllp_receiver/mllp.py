import logging

logger = logging.getLogger("mllp_receiver")

START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"


def wrap_mllp(message: str) -> bytes:
    """Wrap an HL7 message string in MLLP framing for sending."""
    message_bytes = message.encode('utf-8')
    return START_BLOCK + message_bytes + END_BLOCK + CARRIAGE_RETURN


def extract_mllp_payload(raw_bytes: bytes) -> str:
    """
    Extract the HL7 payload from MLLP-framed bytes.
    Raises ValueError if the frame is malformed.
    """
    if not raw_bytes.startswith(START_BLOCK):
        logger.error("Malformed MLLP frame: missing start block (0x0B)")
        raise ValueError("Malformed MLLP frame: missing start block")

    end_index = raw_bytes.find(END_BLOCK)
    if end_index == -1:
        logger.error("Malformed MLLP frame: missing end block (0x1C)")
        raise ValueError("Malformed MLLP frame: missing end block")

    payload_bytes = raw_bytes[1:end_index]
    payload = payload_bytes.decode('utf-8')

    logger.debug(f"Extracted MLLP payload of {len(payload)} characters")
    return payload


def read_mllp_message(sock, buffer_size=4096, max_size_bytes=1024 * 1024):
    """
    Read a complete MLLP-framed message from a socket.
    Returns the extracted HL7 payload string, or None if connection closed.
    """
    data = b""
    while True:
        chunk = sock.recv(buffer_size)
        if not chunk:
            # Connection closed by client
            if data:
                logger.warning("Connection closed with incomplete MLLP message")
            return None

        data += chunk

        if len(data) > max_size_bytes:
            logger.error(f"Message exceeds max size of {max_size_bytes} bytes")
            raise ValueError("Message exceeds maximum allowed size")

        if END_BLOCK in data:
            break

    return extract_mllp_payload(data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Test wrap and extract
    sample_message = "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|20260605120000||ADT^A01|MSG00001|P|2.5"

    wrapped = wrap_mllp(sample_message)
    print(f"Wrapped (bytes): {wrapped}")

    extracted = extract_mllp_payload(wrapped)
    print(f"\nExtracted: {extracted}")
    print(f"\nMatch: {extracted == sample_message}")

    # Test malformed frame
    print("\n--- Testing malformed frame ---")
    try:
        extract_mllp_payload(b"NOT_MLLP_FRAMED")
    except ValueError as e:
        print(f"Correctly caught error: {e}")