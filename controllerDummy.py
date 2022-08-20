import serial, time

Machine = "COM3"
# Machine= "/dev/ttyUSB0"
brate = "115200"
serial = serial.Serial(Machine, baudrate=brate, timeout=0.01)

while True:
    if serial.inWaiting() > 0:
        sensorData = serial.read(1)
        print(sensorData)

        while sensorData != b'0':
            serial.write(b'\x80')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x0C')
            sensorData = serial.read(1)
