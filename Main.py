from uiautomator import Device
import xml.etree.ElementTree as ET

device_name = 'emulator-5554'


def get_state():
    xml = d.dump()
    bit_rep = ''
    root = ET.fromstring(xml.encode('utf-8'))
    print root
    for element in root.iter('node'):
        bit_rep += element.get('index')
    return bit_rep

#text, resource_id, xlass,

if __name__ == '__main__':
    d = Device(device_name)
    d.screen.on()
    # d.press.home()
    # d(text="Clock").click()
    print get_state()