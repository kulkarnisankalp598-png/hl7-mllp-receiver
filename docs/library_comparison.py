"""
Quick hands-on comparison of hl7apy vs python-hl7 for parsing HL7 messages.
"""

sample_message = (
    "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|"
    "20260605120000||ADT^A01|MSG00001|P|2.5\r"
    "EVN|A01|20260605120000\r"
    "PID|1||123456^^^MRN||DOE^JOHN"
)

print("="*60)
print("TESTING hl7apy")
print("="*60)

try:
    from hl7apy.parser import parse_message

    msg = parse_message(sample_message.replace('\r', '\r'), validation_level=2)
    print(f"Message type: {msg.msh.message_type.value}")
    print(f"Control ID: {msg.msh.message_control_id.value}")
    print(f"Sending app: {msg.msh.sending_application.value}")
    print(f"Patient ID segment exists: {hasattr(msg, 'pid')}")
    print("hl7apy parsed successfully")
except Exception as e:
    print(f"hl7apy error: {e}")

print("\n" + "="*60)
print("TESTING python-hl7")
print("="*60)

try:
    import hl7

    msg = hl7.parse(sample_message)
    print(f"Message type: {msg.segment('MSH')[9]}")
    print(f"Control ID: {msg.segment('MSH')[10]}")
    print(f"Sending app: {msg.segment('MSH')[3]}")
    print(f"Number of segments: {len(msg)}")
    print("python-hl7 parsed successfully")
except Exception as e:
    print(f"python-hl7 error: {e}")

print("\n" + "="*60)
print("TESTING INVALID MESSAGE (no MSH)")
print("="*60)

invalid_message = "PID|1||123456^^^MRN||DOE^JOHN"

print("\n--- hl7apy with invalid message ---")
try:
    from hl7apy.parser import parse_message
    msg = parse_message(invalid_message, validation_level=2)
    print("Parsed without error (unexpected)")
except Exception as e:
    print(f"hl7apy correctly raised: {type(e).__name__}: {e}")

print("\n--- python-hl7 with invalid message ---")
try:
    import hl7
    msg = hl7.parse(invalid_message)
    print(f"Parsed without raising — msg: {msg}")
except Exception as e:
    print(f"python-hl7 correctly raised: {type(e).__name__}: {e}")