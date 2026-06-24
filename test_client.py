import socket
import sys

START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"


def wrap_mllp(message: str) -> bytes:
    return START_BLOCK + message.encode('utf-8') + END_BLOCK + CARRIAGE_RETURN


def send_message(host, port, message, expected_acks=1):
    """Connect to the receiver, send an MLLP-framed message, and print all expected ACK(s)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")

        wrapped = wrap_mllp(message)
        sock.sendall(wrapped)
        print(f"Sent message ({len(message)} chars)")

        for i in range(expected_acks):
            response = sock.recv(4096)
            ack_payload = response.strip(START_BLOCK + END_BLOCK + CARRIAGE_RETURN)
            print(f"\nReceived ACK {i+1}/{expected_acks}:")
            print(ack_payload.decode('utf-8').replace(chr(13), chr(92) + 'r' + chr(10)))


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 2575

    # Single message test
    print("=== SINGLE MESSAGE TEST ===")
    sample_message = (
        "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|"
        "20260605120000||ADT^A01|MSG00001|P|2.5\r"
        "EVN|A01|20260605120000\r"
        "PID|1||123456^^^MRN||DOE^JOHN"
    )
    send_message(host, port, sample_message, expected_acks=1)

    # Batch message test
    print("\n\n=== BATCH MESSAGE TEST ===")
    batch_message = (
        "FHS|^~\\&|SendingApp|SendingFacility\r"
        "BHS|^~\\&|SendingApp|SendingFacility\r"
        "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|"
        "20260605120000||ADT^A01|MSG00010|P|2.5\r"
        "EVN|A01|20260605120000\r"
        "PID|1||123456^^^MRN||DOE^JOHN\r"
        "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|"
        "20260605120001||ADT^A01|MSG00011|P|2.5\r"
        "EVN|A01|20260605120001\r"
        "PID|1||789012^^^MRN||SMITH^JANE\r"
        "BTS|2\r"
        "FTS|1"
    )
    send_message(host, port, batch_message, expected_acks=2)