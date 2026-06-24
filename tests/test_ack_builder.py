import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mllp_receiver.ack_builder import build_ack, build_aa_ack, build_ae_ack, build_ar_ack

# --- build_ack tests ---

def test_build_ack_aa_contains_msa():
    ack = build_ack("MSG001", ack_code="AA")
    assert "MSA|AA|MSG001" in ack

def test_build_ack_invalid_code_raises():
    with pytest.raises(ValueError, match="Invalid ACK code"):
        build_ack("MSG001", ack_code="XX")

def test_build_ack_contains_msh():
    ack = build_ack("MSG001", ack_code="AA")
    assert ack.startswith("MSH|")

def test_build_ack_ae_includes_err_segment():
    ack = build_ack("MSG001", ack_code="AE", error_text="Something went wrong")
    assert "ERR|Something went wrong" in ack

def test_build_ack_ar_includes_err_segment():
    ack = build_ack("MSG001", ack_code="AR", error_text="Rejected")
    assert "ERR|Rejected" in ack

def test_build_ack_aa_no_err_segment_by_default():
    ack = build_ack("MSG001", ack_code="AA")
    assert "ERR|" not in ack

def test_build_ack_control_id_preserved():
    ack = build_ack("CUSTOM_ID_123", ack_code="AA")
    assert "CUSTOM_ID_123" in ack

# --- build_aa_ack tests ---

def test_build_aa_ack():
    ack = build_aa_ack("MSG001")
    assert "MSA|AA|MSG001" in ack

# --- build_ae_ack tests ---

def test_build_ae_ack_default_message():
    ack = build_ae_ack("MSG001")
    assert "MSA|AE|MSG001" in ack
    assert "ERR|" in ack

def test_build_ae_ack_custom_message():
    ack = build_ae_ack("MSG001", "Custom error text")
    assert "ERR|Custom error text" in ack

# --- build_ar_ack tests ---

def test_build_ar_ack_default_message():
    ack = build_ar_ack("MSG001")
    assert "MSA|AR|MSG001" in ack
    assert "ERR|" in ack

def test_build_ar_ack_custom_message():
    ack = build_ar_ack("MSG001", "Custom rejection reason")
    assert "ERR|Custom rejection reason" in ack