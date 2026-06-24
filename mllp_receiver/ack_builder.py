import logging
from datetime import datetime

logger = logging.getLogger("mllp_receiver")

ACK_CODES = {
    "AA": "Application Accept",
    "AE": "Application Error",
    "AR": "Application Reject",
}


def build_ack(control_id: str, ack_code: str = "AA", error_text: str = "") -> str:
    """
    Build an HL7 ACK message.
    ack_code must be one of AA, AE, AR.
    """
    if ack_code not in ACK_CODES:
        logger.error(f"Invalid ACK code '{ack_code}' — must be one of {list(ACK_CODES.keys())}")
        raise ValueError(f"Invalid ACK code '{ack_code}'")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ack_control_id = f"ACK{control_id}" if control_id else "ACK00000"

    msh = f"MSH|^~\\&|ReceiverApp|ReceiverFacility|SendingApp|SendingFacility|{timestamp}||ACK|{ack_control_id}|P|2.5"
    msa = f"MSA|{ack_code}|{control_id}"

    segments = [msh, msa]

    if ack_code in ("AE", "AR") and error_text:
        err = f"ERR|{error_text}"
        segments.append(err)

    ack_message = "\r".join(segments)
    logger.info(f"Built ACK ({ack_code} — {ACK_CODES[ack_code]}) for control_id={control_id}")
    return ack_message


def build_aa_ack(control_id: str) -> str:
    """Build an Application Accept ACK."""
    return build_ack(control_id, ack_code="AA")


def build_ae_ack(control_id: str, error_text: str = "Application error processing message") -> str:
    """Build an Application Error ACK."""
    return build_ack(control_id, ack_code="AE", error_text=error_text)


def build_ar_ack(control_id: str, error_text: str = "Message rejected") -> str:
    """Build an Application Reject ACK."""
    return build_ack(control_id, ack_code="AR", error_text=error_text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("--- AA ACK ---")
    ack = build_aa_ack("MSG00001")
    print(ack.replace("\r", "\\r\n"))

    print("\n--- AE ACK ---")
    ack = build_ae_ack("MSG00002", "Missing required PID segment")
    print(ack.replace("\r", "\\r\n"))

    print("\n--- AR ACK ---")
    ack = build_ar_ack("MSG00003", "Unsupported message type")
    print(ack.replace("\r", "\\r\n"))

    print("\n--- Invalid ACK code ---")
    try:
        build_ack("MSG00004", ack_code="XX")
    except ValueError as e:
        print(f"Correctly caught error: {e}")