import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mllp_receiver.hl7_parser import (
    extract_basic_fields,
    is_batch_message,
    split_batch_messages,
    parse_with_hl7apy,
    split_batch_messages_hl7apy
)

SAMPLE_SINGLE = (
    "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|"
    "20260605120000||ADT^A01|MSG00001|P|2.5\r"
    "EVN|A01|20260605120000\r"
    "PID|1||123456^^^MRN||DOE^JOHN"
)

SAMPLE_BATCH = (
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

INVALID_MESSAGE = "PID|1||123456^^^MRN||DOE^JOHN"

# --- extract_basic_fields (manual parsing) tests ---

def test_extract_basic_fields_message_type():
    message_type, control_id = extract_basic_fields(SAMPLE_SINGLE)
    assert message_type == "ADT^A01"

def test_extract_basic_fields_control_id():
    message_type, control_id = extract_basic_fields(SAMPLE_SINGLE)
    assert control_id == "MSG00001"

def test_extract_basic_fields_missing_msh():
    with pytest.raises(ValueError, match="Missing MSH segment"):
        extract_basic_fields(INVALID_MESSAGE)

# --- is_batch_message tests ---

def test_is_batch_message_true_for_fhs():
    assert is_batch_message(SAMPLE_BATCH) == True

def test_is_batch_message_false_for_single():
    assert is_batch_message(SAMPLE_SINGLE) == False

def test_is_batch_message_true_for_bhs_only():
    bhs_only = "BHS|^~\\&|App|Fac\rMSH|^~\\&|App|Fac|App2|Fac2|20260605||ADT^A01|MSG001|P|2.5"
    assert is_batch_message(bhs_only) == True

# --- split_batch_messages tests ---

def test_split_batch_messages_count():
    messages = split_batch_messages(SAMPLE_BATCH)
    assert len(messages) == 2

def test_split_batch_messages_first_control_id():
    messages = split_batch_messages(SAMPLE_BATCH)
    message_type, control_id = extract_basic_fields(messages[0])
    assert control_id == "MSG00010"

def test_split_batch_messages_second_control_id():
    messages = split_batch_messages(SAMPLE_BATCH)
    message_type, control_id = extract_basic_fields(messages[1])
    assert control_id == "MSG00011"

def test_split_batch_messages_excludes_wrapper_segments():
    messages = split_batch_messages(SAMPLE_BATCH)
    for msg in messages:
        assert "FHS|" not in msg
        assert "BHS|" not in msg
        assert "BTS|" not in msg
        assert "FTS|" not in msg

# --- parse_with_hl7apy tests ---

def test_parse_with_hl7apy_message_type():
    message_type, control_id, parsed = parse_with_hl7apy(SAMPLE_SINGLE)
    assert message_type == "ADT^A01"

def test_parse_with_hl7apy_control_id():
    message_type, control_id, parsed = parse_with_hl7apy(SAMPLE_SINGLE)
    assert control_id == "MSG00001"

def test_parse_with_hl7apy_invalid_message():
    with pytest.raises(ValueError, match="hl7apy parsing error"):
        parse_with_hl7apy(INVALID_MESSAGE)

def test_parse_with_hl7apy_returns_parsed_object():
    message_type, control_id, parsed = parse_with_hl7apy(SAMPLE_SINGLE)
    assert parsed is not None

# --- split_batch_messages_hl7apy tests ---

def test_split_batch_messages_hl7apy_count():
    results = split_batch_messages_hl7apy(SAMPLE_BATCH)
    assert len(results) == 2

def test_split_batch_messages_hl7apy_all_valid():
    results = split_batch_messages_hl7apy(SAMPLE_BATCH)
    assert all(r['valid'] for r in results)

def test_split_batch_messages_hl7apy_control_ids():
    results = split_batch_messages_hl7apy(SAMPLE_BATCH)
    control_ids = [r['control_id'] for r in results]
    assert control_ids == ["MSG00010", "MSG00011"]

def test_split_batch_messages_hl7apy_handles_invalid_message_in_batch():
    bad_batch = (
        "FHS|^~\\&|App|Fac\r"
        "BHS|^~\\&|App|Fac\r"
        "MSH|^~\\&|App|Fac|App2|Fac2|20260605||ADT^A01|MSG001|P|2.5\r"
        "EVN|A01|20260605\r"
        "BTS|1\r"
        "FTS|1"
    )
    results = split_batch_messages_hl7apy(bad_batch)
    assert len(results) >= 1