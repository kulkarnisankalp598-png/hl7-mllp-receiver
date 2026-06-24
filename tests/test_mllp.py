import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mllp_receiver.mllp import wrap_mllp, extract_mllp_payload, START_BLOCK, END_BLOCK, CARRIAGE_RETURN

# --- wrap_mllp tests ---

def test_wrap_mllp_adds_start_block():
    result = wrap_mllp("TEST")
    assert result.startswith(START_BLOCK)

def test_wrap_mllp_adds_end_block_and_cr():
    result = wrap_mllp("TEST")
    assert result.endswith(END_BLOCK + CARRIAGE_RETURN)

def test_wrap_mllp_preserves_content():
    result = wrap_mllp("HELLO")
    assert b"HELLO" in result

# --- extract_mllp_payload tests ---

def test_extract_mllp_payload_valid():
    wrapped = wrap_mllp("TEST MESSAGE")
    extracted = extract_mllp_payload(wrapped)
    assert extracted == "TEST MESSAGE"

def test_extract_mllp_payload_missing_start_block():
    bad_frame = b"TEST" + END_BLOCK + CARRIAGE_RETURN
    with pytest.raises(ValueError, match="missing start block"):
        extract_mllp_payload(bad_frame)

def test_extract_mllp_payload_missing_end_block():
    bad_frame = START_BLOCK + b"TEST"
    with pytest.raises(ValueError, match="missing end block"):
        extract_mllp_payload(bad_frame)

def test_extract_mllp_payload_roundtrip():
    original = "MSH|^~\\&|App|Fac|App2|Fac2|20260605||ADT^A01|MSG001|P|2.5"
    wrapped = wrap_mllp(original)
    extracted = extract_mllp_payload(wrapped)
    assert extracted == original

def test_extract_mllp_payload_empty_message():
    wrapped = wrap_mllp("")
    extracted = extract_mllp_payload(wrapped)
    assert extracted == ""