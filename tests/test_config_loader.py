import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mllp_receiver.config_loader import load_config, validate_listener


def write_temp_config(config_dict):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(config_dict, f)
    f.close()
    return f.name


# --- validate_listener tests ---

def test_validate_listener_valid():
    listener = {"name": "Test", "ipAddress": "0.0.0.0", "port": 2575}
    assert validate_listener(listener) == True

def test_validate_listener_missing_name():
    listener = {"ipAddress": "0.0.0.0", "port": 2575}
    assert validate_listener(listener) == False

def test_validate_listener_missing_ip():
    listener = {"name": "Test", "port": 2575}
    assert validate_listener(listener) == False

def test_validate_listener_missing_port():
    listener = {"name": "Test", "ipAddress": "0.0.0.0"}
    assert validate_listener(listener) == False

def test_validate_listener_port_not_int():
    listener = {"name": "Test", "ipAddress": "0.0.0.0", "port": "2575"}
    assert validate_listener(listener) == False

# --- load_config tests ---

def test_load_config_valid_file():
    config = {
        "application": {"name": "TestApp", "logLevel": "INFO"},
        "listeners": [
            {"name": "Listener1", "ipAddress": "0.0.0.0", "port": 2575}
        ]
    }
    path = write_temp_config(config)
    try:
        app_config, listeners = load_config(path)
        assert app_config["name"] == "TestApp"
        assert len(listeners) == 1
    finally:
        os.unlink(path)

def test_load_config_skips_invalid_listener():
    config = {
        "application": {"name": "TestApp"},
        "listeners": [
            {"name": "Good", "ipAddress": "0.0.0.0", "port": 2575},
            {"name": "Bad", "ipAddress": "0.0.0.0"}  # missing port
        ]
    }
    path = write_temp_config(config)
    try:
        app_config, listeners = load_config(path)
        assert len(listeners) == 1
        assert listeners[0]["name"] == "Good"
    finally:
        os.unlink(path)

def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_file.json")

def test_load_config_invalid_json():
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    f.write("{ this is not valid json")
    f.close()
    try:
        with pytest.raises(json.JSONDecodeError):
            load_config(f.name)
    finally:
        os.unlink(f.name)

def test_load_config_empty_listeners():
    config = {"application": {"name": "TestApp"}, "listeners": []}
    path = write_temp_config(config)
    try:
        app_config, listeners = load_config(path)
        assert len(listeners) == 0
    finally:
        os.unlink(path)

def test_load_config_real_file():
    app_config, listeners = load_config("config.json")
    assert len(listeners) == 2
    assert listeners[0]["name"] == "ADTListener"