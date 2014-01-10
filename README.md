BLE-SensorTag-OAD
=================

Simple examples to explore your SensorTag on your laptop:

ble.py is the basic operation BLE peripheral.

sensortag.py is an example of discovering and playing with all attributes on a BLE peripheral.

oad.py is an example of OAD Manager. Now you don't need the lastest smartphone or a TI BLE dongle to update your tag.

I don't have a cc-debuger, I can't even imagine messing with IMG-A. So, how do I update IMG-B while running IMG-B?
No way!!!
oad.invalidate() distroys IMG-B, on the next boot, IMG-A is running, and you are free to update IMG-B now!
To support oad.invalidate(), the OAD profile of IMG-B need to be changed, see firmeware/oad.patch for more information.
