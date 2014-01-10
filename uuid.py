def stduuid(id):
    '''(str)->str

    Return a standard uuid covert from the short id.
    '''
    return ''.join(('0000', id, '-0000-1000-8000-00805f9b34fb'))

def is_stduuid(id):
    '''(str)->boolean

    Return True if id is a standard uuid, otherwise False.
    '''
    return id.startswith('0000') and \
        id.endswith('-0000-1000-8000-00805f9b34fb')

def tiuuid(id):
    '''(str)->str

    Return a private uuid covert from the short id.
    '''
    return ''.join(('f000', id, '-0451-4000-b000-000000000000'))

def is_tiuuid(id):
    '''(str)->boolean

    Return True if id is a private uuid, otherwise False.
    '''
    return id.startswith('f000') and \
        id.endswith('-0451-4000-b000-000000000000')

def shortuuid(uuid):
    '''(str)->str

    Return a short id covert from the standard or private uuid.
    '''
    if is_stduuid(uuid):
        return uuid[4:8]
    else:
        return uuid

'''
{} of uuid-description pairs
'''
uuid_desc = { stduuid('1800'):'<<Generic Access Profile>>',
		 stduuid('1801'):'<<Generic Attribute Profile>>',
		 stduuid('2800'):'<<Primary Service>>',
		 stduuid('2801'):'<<Secondary Service>>',
		 stduuid('2802'):'<<Include>>',
		 stduuid('2803'):'<<Characteristic>>',
		 stduuid('2900'):'<<Characteristic Extended Properties>>',
		 stduuid('2901'):'<<Characteristic User Description>>',
		 stduuid('2902'):'<<Client Characteristic Configuration>>',
		 stduuid('2903'):'<<Server Characteristic Configuration>>',
		 stduuid('2904'):'<<Characteristic Format>>',
		 stduuid('2905'):'<<Characteristic Aggregate Format>>',
		 stduuid('2a00'):'<<Device Name>>',
		 stduuid('2a01'):'<<Appearance>>',
		 stduuid('2a02'):'<<Periphernal Privacy Flag>>',
		 stduuid('2a03'):'<<Reconnection Address>>',
		 stduuid('2a04'):'<<Periphernal Preferred Connection Parameters>>',
		 stduuid('2a05'):'<<Service Changed>>',
		 stduuid('1811'):'<<Alert Notification Service>>',
		 stduuid('180f'):'<<Battery Service>>',
		 stduuid('1810'):'<<Blood Pressure>>',
		 stduuid('1805'):'<<Current Time Service>>',
		 stduuid('1818'):'<<Cycling Power>>',
		 stduuid('1816'):'<<Cycling Speed and Candence>>',
		 stduuid('180a'):'<<Device Information>>',
		 stduuid('1808'):'<<Glucose>>',
		 stduuid('1809'):'<<Health Thermometer>>',
		 stduuid('180d'):'<<Heart Rate>>',
		 stduuid('1812'):'<<Human Interface Device>>',
		 stduuid('1802'):'<<Immediate Alert>>',
		 stduuid('1803'):'<<Link Loss>>',
		 stduuid('1819'):'<<Location and Navigation>>',
		 stduuid('1807'):'<<Next DST Change Service>>',
		 stduuid('180e'):'<<Phone Alert Status Service>>',
		 stduuid('1806'):'<<Reference Time Update Service>>',
		 stduuid('1814'):'<<Running Speed and Candence>>',
		 stduuid('1813'):'<<Scan Parameters>>',
		 stduuid('1804'):'<<Tx Power>>',

		 tiuuid('aa00'):'<<SensorTag Temperature Service>>',
		 tiuuid('aa10'):'<<SensorTag Accelerometer Service>>',
		 tiuuid('aa20'):'<<SensorTag Humidity Service>>',
		 tiuuid('aa30'):'<<SensorTag Magnetometer Service>>',
		 tiuuid('aa40'):'<<SensorTag Barometer Service>>',
		 tiuuid('aa50'):'<<SensorTag Gyroscope Service>>',
		 tiuuid('aa60'):'<<SensorTag Test Service>>',
		 tiuuid('ffc0'):'<<SensorTag OAD Service>>',
		 stduuid('ffe0'):'<<SensorTag Simple Keys Service>>',

		}

def uuid_to_desc(uuid):
    '''(str)->str

    Return the description for an uuid.
    '''
    if uuid in uuid_desc:
		return uuid_desc[uuid]
    else:
    	return ''

def desc_to_uuid(desc):
    '''(str)->str

    Return the uuid from a description.
    '''
    for item in uuid_desc:
		if uuid_desc[item] == desc:
			return item
    return ''
