from uuid import *
import ble
import math
import struct
import tkFileDialog

def invalidate():
    '''()->None

    Invalidate the running firmware.
    '''

    '''
    Find and connect the SensorTag.
    '''
    tag = ble.device()
    if not (tag.find('SensorTag') and tag.connect()):
        print('Fail to connect the SensorTag')
        return

    '''
    Discover the OAD Service.
    '''
    service = tag.discover_service(
                    desc_to_uuid('<<SensorTag OAD Service>>'))
    if service == None:
        print('Fail to discover the OAD service')
        return

    '''
    Discover the invalidate charactristic of the OAD Service.
    '''
    invalidate = tag.discover_characteristic(service, tiuuid('ffc3'))
    if invalidate == None:
        print('Fail to discover the invalidate characteristic of the OAD Service')
        return

    '''
    Invalidate the running firmware
    '''
    tag.char_write_cmd(invalidate.value, 'EEEE')

    print('Invalidate Done')

def update():
    '''()->None

    Update the firmware.
    '''

    '''
    Find and connect the SensorTag.
    '''
    tag = ble.device()
    if not (tag.find('SensorTag') and tag.connect()):
        print('Fail to connect the SensorTag')
        return

    '''
    Discover the OAD Service.
    '''
    service = tag.discover_service(
                    desc_to_uuid('<<SensorTag OAD Service>>'))
    if service == None:
        print('Fail to discover the OAD service')
        return

    '''
    Discover the charactristics of the OAD Service.
    '''
    identify = tag.discover_characteristic(service, tiuuid('ffc1'))
    block = tag.discover_characteristic(service, tiuuid('ffc2'))
    if identify == None or block == None:
        print('Fail to discover the characteristics of the OAD Service')
        return

    '''
    Discover the char_descs of the OAD Service.

    '''
    ccc_identify = tag.discover_char_desc(identify,
                        desc_to_uuid('<<Client Characteristic Configuration>>'))
    ccc_block = tag.discover_char_desc(block,
                        desc_to_uuid('<<Client Characteristic Configuration>>'))
    if ccc_identify == None or ccc_block == None:
        print('Fail to discover the char_descs of the OAD Service')
        return

    '''
    Read the firmware version of the SensorTag
    '''
    tag.char_write_req(ccc_identify.handle, '0100')
    handle, value = tag.char_write_expect_notificition(identify.value,
                            '0000000058585858')
    if handle == None or value == None:
        print('Fail to read the firmware version from the SensorTag')
        return

    firmware_version = value[1] * 256 + value[0]


    '''
    Open the bin file.
    '''
    file = tkFileDialog.askopenfile('rb')
    if file == None:
        print('Fail to open the bin file')
        return

    '''
    Read the header from file.
    '''
    file.seek(4)
    header = file.read(8)
    version, length, uid = struct.unpack('2H4s', header)
    header = header.encode('hex')

    '''
    Check the firmware version.
    '''
    if (version & 0x01) == (firmware_version & 0x01):
        print("The running firmware can't be updated!")
        return

    '''
    Confirm update.
    '''
    print('Current firmeware version is {0}, new firmeware version is \
            {1}'.format(firmware_version, version))
    s = raw_input('Input yes to continue:')
    if s.lower() != 'yes':
        return

    '''
    Start update
    '''
    tag.char_write_req(ccc_block.handle, '0100')
    handle, value = tag.char_write_expect_notificition(identify.value, header)

    if handle == None or value == None:
        print('Fail to start update.')
        return

    if handle != block.value:
        print('Update canceled by the SensorTag.')
        return

    total = math.ceil(length / 4)
    number = value[1] * 256 + value[0]

    '''
    Send blocks
    '''
    while(handle == block.value and value != None and number < total):
        '''
        Calculate the block to send.
        '''
        number = value[1] * 256 + value[0]
        '''
        Read one block to send.
        '''
        file.seek(number * 16)
        blk = file.read(16).encode('hex')
        blk = '{0:02x}{1:02x}{2}'.format(number % 256, number / 256, blk)
        '''
        Send the block.
        '''
        print ('Update block #{0} of #{1}'.format(number, total))
        handle, value = tag.char_write_expect_notificition(block.value, blk)

    if number != total:
        print('Fail to update the firmware.')
        return

    '''
    Close file
    '''
    close(file)

    print('Update done')
if __name__ == '__main__':
    update()
    #invalidate()
