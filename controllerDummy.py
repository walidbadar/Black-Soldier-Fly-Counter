import serial, time
x = 0
Machine = "COM3"
# Machine= "/dev/ttyUSB0"
brate = "115200"
serial = serial.Serial(Machine, baudrate=brate, timeout=0.001)

while True:
    if serial.inWaiting() > 0:
        sensorData = serial.read(1)
        print(sensorData)

        while sensorData != b'0':
            x=x+1
            print(x)
            serial.write(b'\x80')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            serial.write(b'\x00')
            sensorData = serial.read(1)
