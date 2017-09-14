import logging
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_state(device):
    def get_bit_rep():
        xml = device.dump(compressed=False)
        root = ET.fromstring(xml.encode('utf-8'))
        bit_rep = ''
        for element in root.iter('node'):
            bit_rep += element.get('index')
        return bit_rep

    # Assumes that there is a consecutive index from 0 to 32 within dump itself
    a = '01234567891011121314151617181920212223242526272829303132'

    if a in get_bit_rep():
        device.press.back()

    return get_bit_rep()[-20:]