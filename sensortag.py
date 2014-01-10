import ble
from uuid import *

def sensortag_display_services():
    '''
    Find and connect the SensorTag.
    '''
    tag = ble.device()
    if tag.find('SensorTag') and tag.connect():
        '''
        Discover all services.
        '''
        tag.discover_service()

        '''
        Display the tag.
        '''
        print(tag)

        '''
        Disconnect the SensorTag.
        '''
        tag.disconnect()

def sensortag_display_handles():
    '''
    Find and connect the SensorTag.
    '''
    tag = ble.device()
    if tag.find('SensorTag') and tag.connect():
        '''
        Discover all services.
        '''
        tag.discover_service()

        '''
        Discover all characteristics for each service.
        '''
        for ss in tag.services:
            s = tag.services[ss]
            tag.discover_characteristic(s)
            '''
            Discover all char_descs for each characteristic.
            '''
            for cc in s.chars:
                c = s.chars[cc]
                tag.discover_char_desc(c)

        '''
        Display the tag.
        '''
        print(tag)

        '''
        Disconnect the SensorTag.
        '''
        tag.disconnect()

def sensortag_display_service(uuid):
    '''
    Find and connect the SensorTag.
    '''
    tag = ble.device()
    if tag.find('SensorTag') and tag.connect():
        '''
        Discover the service.
        '''
        s = tag.discover_service(uuid)

        '''
        Discover all characteristics for the service.
        '''
        tag.discover_characteristic(s)

        '''
        Discover all char_descs for each characteristic.
        '''
        for cc in s.chars:
            c = s.chars[cc]
            tag.discover_char_desc(c)

        '''
        Display the tag.
        '''
        print(tag)

        '''
        Disconnect the SensorTag.
        '''
        tag.disconnect()

def sensortag_read_temperature():
    '''
    Find and connect the SensorTag.
    '''
    tag = ble.device()
    if tag.find('SensorTag') and tag.connect():
        '''
        Discover the Temperature Service.
        '''
        service = tag.discover_service(
                        desc_to_uuid('<<SensorTag Temperature Service>>'))
        '''
        Discover the config and data charactristics
        '''
        conf = tag.discover_characteristic(service, tiuuid('aa02'))
        data = tag.discover_characteristic(service, tiuuid('aa01'))

        if conf == None or data == None:
            return

        '''
        Read data while temperature sensor is off.
        '''
        print(tag.char_read(data.value))
        '''
        Turn on the temperature sensor.
        '''
        tag.char_write_req(conf.handle, '01')
        '''
        Read data while temperature sensor is on.
        '''
        print(tag.char_read(data.value))
        '''
        Turn off the temperature sensor.
        '''
        tag.char_write_req(conf.handle, '00')

        '''
        Disconnect the SensorTag.
        '''
        tag.disconnect()

if __name__ == '__main__':
    #sensortag_display_services()
    #sensortag_display_service(tiuuid('ffc0'))
    #sensortag_display_handles()
    sensortag_read_temperature()

