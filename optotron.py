#!/usr/bin/env python3
import serial
import os

_serial = None


def close_connection():
    if _serial is not None:
        _serial.close()


def _init():
    global _serial
    try:
        _serial = serial.Serial(os.getenv('DEVICE'), baudrate=9600, timeout=1, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, xonxoff=False)
    except serial.serialutil.SerialException:
        raise Exception('Serial device not connected')


def _do(cmd: str, value: str):
    global _serial
    if _serial is None:
        _init()
    txt = b'~00' + cmd.encode() + b' ' + value.encode() + b'\r'
    try:
        _serial.write(txt)
    except serial.serialutil.SerialException:
        close_connection()
        _init()
        _serial.write(txt)

    txt = _serial.readline()
    res = next(
        (c for c in txt.split(b'\r') if not c.startswith(b'INFO') and c != b''),
        None
    )
    assert res is not None, 'Request(cmd={}, value={}) => No matching response text: "{}"'.format(cmd, value, txt.decode())
    assert res != b'F', 'Request(cmd={}, value={}) failed: "{}"'.format(cmd, value, txt.decode())
    if res[:2] == b'OK':
        return res[2:].decode()
    if res[:1] == b'P':
        return res[1:].decode()
    raise Exception('Request(cmd={}, value={}) => Response does not starts with OK or P: "{}"'.format(cmd, value, txt.decode()))


def is_power_on():
    return _do('124', '1') == '1'


def power_on():
    _do('00', '1')


def power_off():
    _do('00', '0')


def mute():
    _do('03', '1')


def unmute():
    _do('03', '0')


def set_volume(value: int):
    assert 0 <= value <= 10, 'Volume out of range'
    _do('81', str(value))


def dec_volume():
    _do('140', '17')


def inc_volume():
    _do('140', '18')


def press_enter_btn():
    _do('140', '12')


def press_menu_btn():
    _do('140', '20')


def set_background_color(color: str):
    colors = ['blue', 'black', 'red', 'green', 'white']
    assert color in colors, 'Unknown color'
    _do('104', str(colors.index(color)+1))
    press_menu_btn()


def get_lamp_hours():
    return int(_do('108', '1'))


def set_input_source(src: str):
    assert src in ['hdmi', 'vga', 'video']
    if src == 'hdmi':
        _do('12', '1')
    elif src == 'vga':
        _do('12', '5')
    elif src == 'video':
        _do('12', '10')
