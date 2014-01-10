from uuid import *
import pexpect
import re
import time

class char_desc:
    '''
    charachteristic description class.
    '''

    def __init__(self, handle, uuid):
        '''(char_desc, int, str)->None

        Init this char_desc.
        '''
        self.handle = handle
        self.uuid = uuid

    def __str__(self):
        '''(char_desc)->str

        Covert this char_desc to a str.
        '''
        return '\t\t0x{0:04x}\t{1}\t{2}\n'.format(self.handle, self.uuid,
                                            uuid_to_desc(self.uuid))

class characteristic:
    '''
    charachteristic class.
    '''

    def __init__(self, handle, properties, value, uuid):
        '''(characteristic, int, int, int, str)->None

        Init this characteristic.
        '''
        self.properties = properties
        self.handle = handle
        self.value = value
        self.uuid = uuid
        self.end = 0xffff
        self.descs = {}

    def __str__(self):
        '''(characteristic)->str

        Covert this characteristic to a str.
        '''

        '''
        Covert properties to a str.
        '''
        p = self.properties
        o = 'BRwWNIAE'
        s = '0x{0:02x}('.format(p)
        for i in range(8):
            if(p & (1 << i)):
                s = s + o[i]
            else:
                s = s + ' '
        s = s + ')'

        '''
        The characteristic itself.
        '''
        ret = '\t0x{0:04x}\t{1}\t{2}\t0x{3:04x}\t0x{4:04x}\t{5}\n'.format( \
                    self.handle, self.uuid, s, self.value, self.end,
                    uuid_to_desc(self.uuid))

        '''
        All char_descs of the characteristic.
        '''
        if len(self.descs) == 0:
            return ret

        ret = ret + '\t\tHandle\tUUID\t\t\t\t\tDescription\n'
        for item in self.descs:
            ret = ret + str(self.descs[item])

        return ret

    def add_char_desc(self, d):
        '''(characteristic, char_desc)->None

        Add a char_desc to this characteristic.
        '''
        if d not in self.descs:
            self.descs[d.uuid] = d

class service:
    '''
    service class.
    '''

    def __init__(self, handle, end, uuid):
        '''(service, int, int, str)->None

        Init this service.
        '''
        self.handle = handle
        self.end = end
        self.uuid= uuid
        self.chars = {}

    def __str__(self):
        '''(service)->str

        Covert this characteristic to a str.
        '''

        '''
        The service itself.
        '''
        ret = '0x{0:04x}\t{1}\t0x{2:04x}\t{3}\n'.format(self.handle,
                self.uuid, self.end, uuid_to_desc(self.uuid))

        '''
        All charactersitcs of this service.
        '''
        if len(self.chars) == 0:
            return ret

        ret = ret + '\tHandle\tUUID\t\t\t\t\t'
        ret = ret + 'Properties\tValue\tEnd\tDescription\n'
        for item in self.chars:
            ret = ret + str(self.chars[item])

        return ret

    def add_characteristic(self, c):
        '''(service, characteristic)->None

        Add a characteristic to this service.
        '''
        if c not in self.chars:
            self.chars[c.uuid] = c

class device:
    '''
    device class, represent a BLE peripheral.
    '''

    def __init__(self):
        '''(device, str)->None

        Init this device.
        '''
        self.name = None
        self.address = None
        self.session = None
        self.services = {}

    def __str__(self):
        '''(device)->str

        Covert this device to str
        '''
        if len(self.services) == 0:
            return None

        '''
        All sercices on this device
        '''
        ret = 'Handle\tUUID\t\t\t\t\tEnd\tDescription\n'
        for item in self.services:
            ret = ret + str(self.services[item])

        return ret

    def scan(self, timeout = 10):
        '''(device, int)->None

        Scan all LE peripherals, stop when timeout.
        '''
        print('Scanning...')

        dev = []
        end_time = time.time() + timeout

        '''
        Stat scan.
        '''
        se = pexpect.spawn('hcitool lescan', timeout = 5)
        patten = '(([\da-fA-F]){2}:){5}([\da-fA-F]){2} .*(?=\r\n)'

        '''
        Read a record.
        '''
        i = se.expect([patten, pexpect.TIMEOUT, pexpect.EOF])
        while i == 0:
            '''
            Scan timeout.
            '''
            if time.time() >= end_time:
                se.sendcontrol('C')

            '''
            Save and print a record.
            '''
            info = se.after
            if not info in dev:
                dev.append(info)
                print(''.join(('\t', info)))

            '''
            Read next record.
            '''
            i = se.expect([patten, pexpect.TIMEOUT, pexpect.EOF])


    def find(self, name, timeout = 10):
        '''(device, str, int)->boolean

        Find an LE peripheral which matches the specified name.
        Init self.name and self.address with the device info.
        '''
        print('Finding...')

        '''
        Start scan
        '''
        se = pexpect.spawn('hcitool lescan', timeout = timeout)
        patten = ''.join(('(([\da-fA-F]){2}:){5}([\da-fA-F]){2}(?= ', name, ')'))

        '''
        Wait for the device.
        '''
        try:
            se.expect(patten)
        except pexpect.TIMEOUT:
            se.sendcontrol('C')
            print('FIND: TIMEOUT')
            return False
        except pexpect.EOF:
            print('FIND: FAILED')
            return False

        '''
        Set the name and address info of this device.
        '''
        self.name = name
        self.address = se.after
        se.sendcontrol('C')

        return True

    def disconnect(self):
        '''(device)->None

        Disconnect this device.
        '''
        if self.session.isalive():
            self.session.sendcontrol('C')
        self.session = None
        self.services = {}

    def connect(self):
        '''(device)->boolean

        Connect to this device. Start the interactive session for gatttool.
        Precondition: self.address != None.
        '''
        if self.address == None:
            print('CONNECT: Device address not specified.')
            return False
        print (''.join(('Connecting to ', self.address, ' ...')))

        '''
        Start gatttool in interactive mode.
        '''
        self.session = pexpect.spawn('gatttool -b {} -I'.format(self.address))
        try:
            '''
            Wait till the gatttool starts.
            '''
            self.session.expect('\[LE\]>')
            '''
            Send 'connect' command.
            '''
            self.session.sendline('connect')
            '''
            Wait till the connect command finish.
            '''
            self.session.expect('Connection successful')
            '''
            Wait for [LE]> or TIMEOUT.
            '''
            self.session.expect('\[LE\]>')

        except pexpect.TIMEOUT:
            self.disconnect()
            print('CONNECT: TIMEOUT')
            return False

        except pexpect.EOF:
            self.disconnect()
            print('CONNECT: FAILED')
            return False

        return True

    def add_service(self, s):
        '''(device, service)->None

        Add a service to this device.
        '''
        if s.uuid not in self.services:
            self.services[s.uuid] = s

    def discover_service(self, uuid = None):
        '''(device, str)->service

        Discover primary services specified by uuid.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('PRIMARY: No peripheral connected.')
            return None

        '''
        Check the service cache first.
        '''
        if uuid != None and uuid in self.services:
            return self.services[uuid]

        '''
        No lucky, perform primary service discovery
        '''
        try:
            '''
            Send 'primary' command.
            '''
            self.session.sendline('primary')
            '''
            Wait till the command finish or TIMEOUT.
            '''
            self.session.expect('\[LE\]>.+\[LE\]>')

        except pexpect.TIMEOUT:
            self.disconnect()
            print('PRIMARY: TIMEOUT')
            return False

        except pexpect.EOF:
            self.disconnect()
            print('PRIMARY: FAILED')
            return False

        '''
        Process the command result.
        Find and save all primary services.
        '''
        p = re.compile('.*(0x[\da-fA-F]{4}).*(0x[\da-fA-F]{4}).*([\da-fA-F]{8}(-[\da-fA-F]{4}){3}-[\da-fA-F]{12})')
        mm = p.findall(self.session.after)
        for m in mm:
            hnd = int(m[0].replace('0x',''), 16)
            end = int(m[1].replace('0x',''), 16)
            s = service(hnd, end, m[2])
            self.add_service(s)

        '''
        Check the service cache again.
        '''
        if uuid != None and uuid in self.services:
            return self.services[uuid]

        return None

    def discover_characteristic(self, service, uuid = None):
        '''(device, service, str)->characteristic

        Discover characteristics specified by uuid in the specified service.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('CHARACTERISTIC: No peripheral connected.')
            return None

        if service == None:
            print('CHARACTERISTIC: No service specified.')
            return None

        '''
        Check the characteristics cache first.
        '''
        if uuid != None and uuid in service.chars:
            return service.chars[uuid]

        '''
        No lucky, perform characteristic discovery
        '''
        cmd = 'characteristics 0x{0:04x} 0x{1:04x}'.format(service.handle,
                    service.end)
        try:
            self.session.sendline(cmd)
            self.session.expect('\[LE\]>.+\[LE\]>')

        except pexpect.TIMEOUT:
            self.disconnect()
            print('CHARACTERISTIC: TIMEOUT')
            return False

        except pexpect.EOF:
            self.disconnect()
            print('CHARACTERISTIC: FAILED')
            return False

        p = re.compile('.*(0x[\da-fA-F]{4}).*(0x[\da-fA-F]{2}).*(0x[\da-fA-F]{4}).*([\da-fA-F]{8}(-[\da-fA-F]{4}){3}-[\da-fA-F]{12})')
        mm = p.findall(self.session.after)
        for m in mm:
            handle = int(m[0].replace('0x', ''), 16)
            properties = int(m[1].replace('0x', ''), 16)
            value = int(m[2].replace('0x', ''), 16)
            c = characteristic(handle, properties, value, m[3])
            service.add_characteristic(c)

        '''
        Calculate the end handle for all characterstics in this service.
        '''
        for i in service.chars:
           service.chars[i].end = service.end
           for n in service.chars:
               if service.chars[i].handle < service.chars[n].handle\
                    < service.chars[i].end:
                        service.chars[i].end = service.chars[n].handle - 1

        '''
        Check the characteristics cache again.
        '''
        if uuid != None and uuid in service.chars:
            return service.chars[uuid]

        return None

    def discover_char_desc(self, characteristic, uuid = None):
        '''(device, characteristic, str)->char_desc

        Discover char_descs specified by uuid in the specified characteristic.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('CHAR_DESC: No peripheral connected.')
            return None

        if service == None:
            print('CHAR_DESC: No characteristic specified.')
            return None

        '''
        Check the char_descs cache first.
        '''
        if uuid != None and uuid in characteristic.descs:
            return characteristic.descs[uuid]

        '''
        No lucky, perform characteristic discovery
        '''
        start = characteristic.value + 1
        end = characteristic.end

        cmd = 'char-desc 0x{0:04x} 0x{1:04x}'.format(start, end)
        try:
            self.session.sendline(cmd)
            self.session.expect('\[LE\]>.+\[LE\]>')

        except pexpect.TIMEOUT:
            self.disconnect()
            print('CHAR_DESC: TIMEOUT')
            return False

        except pexpect.EOF:
            self.disconnect()
            print('CHAR_DESC: FAILED')
            return False

        p = re.compile('.*(0x[\da-fA-F]{4}).*([\da-fA-F]{4})')
        mm = p.findall(self.session.after)
        for m in mm:
            handle = int(m[0].replace('0x', ''), 16)
            id = stduuid(m[1])
            cd = char_desc(handle, id)
            characteristic.add_char_desc(cd)

        '''
        Check the char_descs cache again.
        '''
        if uuid != None and uuid in characteristic.descs:
            return characteristic.descs[uuid]

        return None

    def char_read(self, handle):
        '''(device, int)->[int]

        Read a handle.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('CHAR_READ: No peripheral connected.')
            return None

        cmd = 'char-read-hnd 0x{0:04x}'.format(handle)
        try:
            self.session.sendline(cmd)
            self.session.expect('\[LE\]>.*\[LE\]>')

        except pexpect.TIMEOUT:
            self.disconnect()
            print('\tCHAR_READ: TIMEOUT')
            return value

        except pexpect.EOF:
            self.disconnect()
            print('\tCHAR_READ: FAILED')
            return value

        p = re.compile(' ([\da-fA-F]{2})')
        m= p.findall(self.session.after)

        return [int(i, 16) for i in m]

    def char_write_req(self, handle, value):
        '''(device, int, int)->boolean

        Write a handle.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('CHAR_WRITE_REQ: No peripheral connected.')
            return None

        cmd = 'char-write-req 0x{0:04x} {1}'.format(handle, value)

        try:
            self.session.sendline(cmd)
            self.session.expect('\[LE\]>.*\[LE\]>')

        except pexpect.TIMEOUT:
            self.disconnect()
            print('\tCHAR_WRITE_REQ: TIMEOUT')
            return False

        except pexpect.EOF:
            self.disconnect()
            print('\tCHAR_WRITE_REQ: FAILED')
            return False

        p = re.compile('success')
        m= p.findall(self.session.after)

        if m == []:
            return False

        return True

    def char_write_cmd(self, handle, value):
        '''(device, int, int)->boolean

        Write a handle without response.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('CHAR_WRITE_CMD: No peripheral connected.')
            return None

        cmd = 'char-write-cmd 0x{0:04x} {1}'.format(handle, value)
        try:
            self.session.sendline(cmd)
            self.session.expect('\[LE\]>.*\[LE\]>')
        except pexpect.TIMEOUT:
            self.disconnect()
            print('\tCHAR_WRITE_CMD: TIMEOUT')
            return False
        except pexpect.EOF:
            self.disconnect()
            print('\tCHAR_WRITE_CMD: FAILED')
            return False

        return True

    def char_write_expect_notificition(self, handle, value):
        '''(device, int, int)->(int, []) of handle-value pairs

        Write a handle without response, and wait for a notification.
        Precondition: self.session != None.
        '''
        if self.session == None:
            print('CHAR_WRITE_EXPECT_NOTIFICATION: No peripheral connected.')
            return None

        cmd = 'char-write-cmd 0x{0:04x} {1}'.format(handle, value)
        try:
            self.session.sendline(cmd)
            self.session.expect('Notification handle = 0x([\da-fA-F]{4}) value: .*\r\n')
        except pexpect.TIMEOUT:
            print('\tCHAR_WRITE_EXPECT_NOTIFICATION: TIMEOUT')
            return None, None
        except pexpect.EOF:
            self.disconnect()
            print('\tCHAR_WRITE_EXPECT_NOTIFICATION: FAILED')
            return None, None

        p = re.compile('Notification handle = 0x([\da-fA-F]{4}) value: ')
        m= p.findall(self.session.after)
        if m == []:
            return None, None

        handle = int(m[0], 16)
        p = re.compile(' ([\da-fA-F]{2})')
        m= p.findall(self.session.after)
        if m == []:
            return None, None

        return (handle, [int(i, 16) for i in m])
