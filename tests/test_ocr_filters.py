from ocr_engine import SERIAL, DATE

def test_serial_and_date_patterns():
    assert SERIAL.fullmatch('033788')
    assert not SERIAL.fullmatch('21.08.2026')
    assert SERIAL.fullmatch('92026')  # ambiguous: must be rejected by column context, not regex alone
    assert DATE.search('21.08.2026')
