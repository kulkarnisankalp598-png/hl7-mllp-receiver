import socket
import threading
import logging

from mllp_receiver.mllp import read_mllp_message, wrap_mllp
from mllp_receiver.hl7_parser import extract_basic_fields, is_batch_message, split_batch_messages
from mllp_receiver.ack_builder import build_aa_ack, build_ae_ack, build_ar_ack

logger = logging.getLogger("mllp_receiver")


def handle_client(client_socket, client_address, listener_name):
    """Handle a single client connection — read messages, process, send ACKs."""
    logger.info(f"[{listener_name}] Client connected: {client_address}")

    try:
        while True:
            try:
                payload = read_mllp_message(client_socket)
            except ValueError as e:
                logger.error(f"[{listener_name}] Malformed MLLP frame from {client_address}: {e}")
                continue

            if payload is None:
                logger.info(f"[{listener_name}] Client disconnected: {client_address}")
                break

            process_message(client_socket, payload, listener_name)

    except Exception as e:
        logger.error(f"[{listener_name}] Unexpected error handling client {client_address}: {e}", exc_info=True)
    finally:
        client_socket.close()
        logger.info(f"[{listener_name}] Connection closed: {client_address}")


def process_message(client_socket, payload, listener_name):
    """Process a received HL7 payload — single or batch — and send ACK(s)."""
    try:
        if is_batch_message(payload):
            logger.info(f"[{listener_name}] Batch message detected")
            messages = split_batch_messages(payload)
            for msg in messages:
                process_single_message(client_socket, msg, listener_name)
        else:
            process_single_message(client_socket, payload, listener_name)

    except Exception as e:
        logger.error(f"[{listener_name}] Error processing message: {e}", exc_info=True)
        ack = build_ae_ack("UNKNOWN", str(e))
        client_socket.sendall(wrap_mllp(ack))


def process_single_message(client_socket, message, listener_name):
    """Parse a single HL7 message, log metadata, and send ACK."""
    try:
        message_type, control_id = extract_basic_fields(message)
        logger.info(f"[{listener_name}] Received message — type={message_type}, control_id={control_id}")

        ack = build_aa_ack(control_id)
        client_socket.sendall(wrap_mllp(ack))
        logger.info(f"[{listener_name}] Sent AA ACK for control_id={control_id}")

    except ValueError as e:
        logger.error(f"[{listener_name}] Failed to parse message: {e}")
        ack = build_ar_ack("UNKNOWN", str(e))
        client_socket.sendall(wrap_mllp(ack))


def start_listener(name, ip_address, port, **kwargs):
    """Start a TCP listener on the given IP and port. Runs forever, accepting clients."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ip_address, port))
        server_socket.listen(5)
        logger.info(f"[{name}] Listening on {ip_address}:{port}")

    except OSError as e:
        logger.error(f"[{name}] Failed to bind to {ip_address}:{port} — {e}")
        return

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address, name),
                daemon=True
            )
            client_thread.start()
        except Exception as e:
            logger.error(f"[{name}] Error accepting connection: {e}", exc_info=True)


def start_all_listeners(listeners):
    """Start one thread per configured listener."""
    threads = []
    for listener in listeners:
        t = threading.Thread(
            target=start_listener,
            kwargs={
                'name': listener['name'],
                'ip_address': listener['ipAddress'],
                'port': listener['port']
            },
            daemon=True
        )
        t.start()
        threads.append(t)
        logger.info(f"Started thread for listener '{listener['name']}'")
    return threads