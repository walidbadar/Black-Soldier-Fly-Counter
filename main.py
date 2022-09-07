# import the necessary packages
from tkinter import *
from pyzbar import pyzbar
from datetime import datetime
import cv2, requests, shutil, time, serial, binascii, threading, math, io, os, csv

if os.name == 'nt':
    comPort = 'COM4'
    path = 'D:/Softwares/Waleed Docs/Projects/Freelancing/Fiverr/magnetofix (Stefan)/Fly Counter/'
    url = "http://192.168.1.4:8080/shot.jpg"

else:
    comPort = "/dev/ttyUSB0"
    path = '/home/pi/flyCounter/'

    # --------------------------------------------------------------
    # GPIO Setup
    # ---------------------------------------------------------------
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.cleanup()

# --------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------
count = 1
noOfFly = 0
flyCount = 0
NoOfbeamPerFly = 0
preBeam48 = ''
preBeam48Join = ''
QRcode = ''
loveCageQRcode = 'LC1'
darkCageQRcode = 'DC1'
startFlag = 0
loveCageFlag = 0
darkCageFlag = 0
noOfFliesPerMinTimer = ''
logsData = ['', '', '', '', '', '']
logsHeader = ['Date', 'ID of Dark Cage', 'Start Time of Dark Cage', 'End Time of Dark Cage',
              'No. of Flies from Dark Cage', 'Total No. of Flies from Love Cage']


# --------------------------------------------------------------
# No. of Flies per minute timer
# --------------------------------------------------------------
def noOfFliesPerMin():
    global count, noOfFliesPerMinTimer
    print('count', count)
    print('flyCount', flyCount)
    print(datetime.now())

    noOfFliesPerMinTimer = root.after(10000, noOfFliesPerMin)

    if flyCount < (int(newSettingsData[2])) * count:
        print('No Fly Detected within 1 min', datetime.now())
        stop()
    else:
        count = count + 1

# --------------------------------------------------------------
# Serial Data Thread
# --------------------------------------------------------------
sensor = serial.Serial(comPort, baudrate="115200", timeout=0.001)


def read_serial_packet():
    global flyCount, preBeam48, preBeam48Join
    print("Started Serial COM")

    if newSettingsData[4] != '':
        NoOfbeamPerFly = int(newSettingsData[4])

    if not sensor.isOpen():
        sensor.open()
    sensor.write(b'B')
    sensor.flush()

    while True:
        if startFlag:
            # sensor.write(b'B')  # Experimental Case

            if sensor.inWaiting() > 6:
                sensorData = sensor.read(7)
                # sensor.reset_input_buffer()  # Experimental Case
                # sensor.write(b'0')  # Experimental Case
                # sensor.flush()  # Experimental Case

                Byte1 = int(binascii.hexlify(sensorData)[0:2], 16)
                Byte1bin = format(Byte1, '#010b')[4:]  # Beam 43 to 48
                Byte2 = int(binascii.hexlify(sensorData)[2:4], 16)
                Byte2bin = format(Byte2, '#010b')[3:]  # Beam 36 to 42
                Byte3 = int(binascii.hexlify(sensorData)[4:6], 16)
                Byte3bin = format(Byte3, '#010b')[3:]  # Beam 29 to 35
                Byte4 = int(binascii.hexlify(sensorData)[6:8], 16)
                Byte4bin = format(Byte4, '#010b')[3:]  # Beam 21 to 28
                Byte5 = int(binascii.hexlify(sensorData)[8:10], 16)
                Byte5bin = format(Byte5, '#010b')[3:]  # Beam 15 to 21
                Byte6 = int(binascii.hexlify(sensorData)[10:12], 16)
                Byte6bin = format(Byte6, '#010b')[3:]  # Beam 8 to 14
                Byte7 = int(binascii.hexlify(sensorData)[12:14], 16)
                Byte7bin = format(Byte7, '#010b')[3:]  # Beam 1 to 7

                beam = [Byte1, Byte2, Byte3, Byte4, Byte5, Byte6, Byte7]

                if (128 <= beam[0] <= 191) and (0 <= beam[1] <= 127) and (
                        0 <= beam[2] <= 127) and (0 <= beam[3] <= 127) and (
                        0 <= beam[4] <= 127) and (0 <= beam[5] <= 127) and (
                        0 <= beam[6] <= 127):
                    print("Perfect beam")

                    if preBeam48Join != '':
                        preBeam48 = preBeam48Join.getvalue()

                    beamBin = [Byte1bin, Byte2bin, Byte3bin, Byte4bin, Byte5bin, Byte6bin, Byte7bin]
                    beam48 = Byte1bin + Byte2bin + Byte3bin + Byte4bin + Byte5bin + Byte6bin + Byte7bin
                    beam48Split = beam48.split('0')
                    beam48Split = [zero for zero in beam48Split if zero]
                    beam48Join = ''.join(beamBin)
                    print('beam48Join', beam48Join)
                    print("beam48Split: ", beam48Split)

                    preBeam48Join = io.StringIO()
                    preBeam48Join.write(str(beam48Join))

                    if preBeam48 == str(beam48Join):  # Experimental Case
                        print("Same")
                    else:
                        print("Changed")
                        for x in range(len(beam48Split)):
                            flyCountRound = len(beam48Split[x]) / NoOfbeamPerFly
                            if (float(flyCountRound) % 1) > 0:
                                noOfFly = math.ceil(flyCountRound)
                            else:
                                noOfFly = round(flyCountRound)
                            flyCount = noOfFly + flyCount

                        # print("flyCount: ", flyCount)

        else:
            # sensor.close()  # Experimental Case
            break


def main():
    global root

    root = Tk()
    root.overrideredirect(0)
    root.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
    root.resizable(0, 0)
    root.title("Swiss Federal Institute of Aquatic Science and Technology")

    # --------------------------------------------------------------
    # Images
    # --------------------------------------------------------------
    Logophoto = PhotoImage(file="images/#eawag.gif")
    bgphoto = PhotoImage(file="images/bg.gif")

    def keypad(x, y):
        global root
        global entry
        top = Toplevel(root, relief="groove", bd=4)
        top.overrideredirect(1)
        top.wm_geometry('202x180+' + x + '+' + y)  # x,y+origin x+ origin y

        varRow = 3
        varColumn = 0

        buttons1 = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            'DEL', '0', 'ENTER']

        for button in buttons1:

            command = lambda pd=button: select(pd)
            if button == 'DEL':
                Button(top, text=button, width=4, bg="gray", fg="black",
                       activebackground="#ffffff", activeforeground="#3c4987", relief='raised',
                       pady=10, bd=1, command=command).grid(row=varRow, column=varColumn)

            elif button == "ENTER":
                Button(top, text=button, width=4, bg="gray", fg="black",
                       activebackground="#ffffff", activeforeground="#3c4987", relief='raised',
                       pady=10, bd=1, command=top.destroy).grid(row=varRow, column=varColumn)
            else:
                Button(top, text=button, width=4, bg="gray", fg="black",
                       activebackground="#ffffff", activeforeground="#3c4987", relief='raised',
                       pady=10, bd=1, command=command).grid(row=varRow, column=varColumn)

            varColumn += 1

            if varColumn > 2 and varRow == 2:
                varColumn = 0
                varRow += 1
            if varColumn > 2 and varRow == 3:
                varColumn = 0
                varRow += 1
            if varColumn > 2 and varRow == 4:
                varColumn = 0
                varRow += 1
            if varColumn > 2 and varRow == 5:
                varColumn = 0
                varRow += 1

        def select(value):
            global buttons1
            if value == 'DEL':
                entry.delete(len(entry.get()) - 1, END)
            else:
                entry.insert(END, value)

        top.title("Keypad")
        # top.transient(root)
        root.wait_window(top)

    def fillLoveCageQRscan():
        global scanLCstatusLb, QRcode
        fillLoveCageQRscanWin = Toplevel(root)
        fillLoveCageQRscanWin.overrideredirect(0)
        # fillLoveCageQRscanWin.attributes("-toolwindow", 1)
        fillLoveCageQRscanWin.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
        fillLoveCageQRscanWin.resizable(0, 0)
        fillLoveCageQRscanWin.title("Fill Love Cage QR Scan")

        # --------------------------------------------------------------
        # Scan QR-code of Love Cage Label
        # --------------------------------------------------------------
        LogoLb = Label(fillLoveCageQRscanWin, height=1, width=25, text="Scan QR-code of Love Cage",
                       anchor=CENTER,
                       fg="Black", font="Arial 36 bold")
        LogoLb.place(x=10, y=10)

        # --------------------------------------------------------------
        # Scan QR-code of Love Cage Status Label
        # --------------------------------------------------------------
        scanLCstatusLb = Label(fillLoveCageQRscanWin, height=10, width=40,
                               text="Place the Camera in front of Love Cage to\nScan QR code",
                               anchor=CENTER, fg="Black", bg='Grey', relief=RIDGE,
                               font="Arial 15 bold")
        scanLCstatusLb.place(x=125, y=75)

        # --------------------------------------------------------------
        # Scan Button
        # --------------------------------------------------------------
        def loveCageScanQRcode():
            global loveCageFlag, loveCageQRcode

            newLoveCageQRcodeData = []
            with open(path + 'qrCode/' + 'loveCageQRcode.txt') as loveCageQRcodeFile:
                loveCageQRcodeData = loveCageQRcodeFile.readlines()

            for newline in loveCageQRcodeData:
                loveCageQRcodeData = newline.replace("\n", "")
                newLoveCageQRcodeData.append(loveCageQRcodeData)
            print('newLoveCageQRcodeData', newLoveCageQRcodeData)
            print('Lenght of newLoveCageQRcodeData', len(newLoveCageQRcodeData))

            resp = requests.get(url, stream=True)
            local_file = open(path + 'images/' + 'local_image.jpg', 'wb')
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, local_file)

            # subprocess.Popen("libcamera-still -r -o /home/pi/flyCounter/local_image.jpg", shell=True)
            image = cv2.imread(path + 'images/' + 'local_image.jpg', 0)
            barcodes = pyzbar.decode(image)

            if not barcodes:
                loveCageFlag = 0
                loveCageQRcode = ''

            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                loveCageQRcode = barcode.data.decode("utf-8")
                print(loveCageQRcode)

            if loveCageQRcode in newLoveCageQRcodeData:
                loveCageFlag = 1
                for loveCage in range(0, 4):
                    if newLoveCageQRcodeData[loveCage] == loveCageQRcode:
                        print(str(1 + loveCage))
                        scanLCstatusLb.configure(text="Love Cage " + str(1 + loveCage) + " QR Code Detected")

            else:
                scanLCstatusLb.configure(text="Scan QR Code Again for Love Cage")

        scanBtn = Button(fillLoveCageQRscanWin, height=2, width=20, text="Scan QR-code", font='Arial 15 bold',
                         fg="Black", bg='#75CC3D', relief=RAISED,
                         command=lambda: loveCageScanQRcode())
        scanBtn.place(x=100, y=350)

        # --------------------------------------------------------------
        # Next Button for fillLoveCageQRscanWin
        # --------------------------------------------------------------
        def process():
            startProcess()
            fillLoveCageQRscanWin.destroy()

        nextBtn = Button(fillLoveCageQRscanWin, height=2, width=20, text="Next", font='Arial 15 bold',
                         fg="Black", bg='#00A3FF', relief=RAISED,
                         command=lambda: process())
        nextBtn.place(x=400, y=350)

    def setting():
        settinWin = Toplevel(root)
        settinWin.overrideredirect(0)
        # settinWin.attributes("-toolwindow", 1)
        settinWin.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
        settinWin.resizable(0, 0)
        settinWin.title("Setting")

        newSettingsData = []
        with open("settings.txt") as settingsFile:
            settingsData = settingsFile.readlines()

        for newline in settingsData:
            settingsData = newline.replace("\n", "")
            newSettingsData.append(settingsData)
        print(newSettingsData)

        # --------------------------------------------------------------
        # Default Values
        # --------------------------------------------------------------
        LogoLb = Label(settinWin, height=1, width=20, text="Default Values",
                       anchor=NW,
                       fg="Black", font="Arial 15 bold")
        LogoLb.place(x=5, y=50)

        # --------------------------------------------------------------
        # Number of flies from individual dark cage
        # --------------------------------------------------------------
        def fliesPerDarkCageKeyboard():
            global entry

            entry = fliesPerDarkCageTb
            keypad("350", "180")

        fliesPerDarkCageLb = Label(settinWin, height=1, width=8, text="#flies/DC",
                                   anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                                   font="Arial 15 bold")
        fliesPerDarkCageLb.place(x=200, y=5)

        fliesPerDarkCageTb = Entry(settinWin, width=9, font="Arial 15 bold")
        fliesPerDarkCageTb.place(x=200, y=50)
        fliesPerDarkCageTb.bind("<Button-1>", lambda e: fliesPerDarkCageKeyboard())
        fliesPerDarkCageTb.insert(0, newSettingsData[0])

        # --------------------------------------------------------------
        # Time limit
        # --------------------------------------------------------------
        def timeLimitKeyboard():
            global entry

            entry = timeLimitTb
            keypad("350", "180")

        timeLimitLb = Label(settinWin, height=1, width=8, text="Time (min)",
                            anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                            font="Arial 15 bold")
        timeLimitLb.place(x=350, y=5)

        timeLimitTb = Entry(settinWin, width=9, font="Arial 15 bold")
        timeLimitTb.place(x=350, y=50)
        timeLimitTb.bind("<Button-1>", lambda e: timeLimitKeyboard())
        timeLimitTb.insert(0, newSettingsData[1])

        # --------------------------------------------------------------
        # Number of flies per time interval
        # --------------------------------------------------------------
        def fliesPerTimeKeyboard():
            global entry

            entry = fliesPerTimeTb
            keypad("350", "180")

        fliesPerTimeLb = Label(settinWin, height=1, width=8, text="#flies/min",
                               anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                               font="Arial 15 bold")
        fliesPerTimeLb.place(x=500, y=5)

        fliesPerTimeTb = Entry(settinWin, width=9, font="Arial 15 bold")
        fliesPerTimeTb.place(x=500, y=50)
        fliesPerTimeTb.bind("<Button-1>", lambda e: fliesPerTimeKeyboard())
        fliesPerTimeTb.insert(0, newSettingsData[2])

        # --------------------------------------------------------------
        # Total number of flies in love cage
        # --------------------------------------------------------------
        def fliesPerLoveCageKeyboard():
            global entry

            entry = fliesPerLoveCageTb
            keypad("350", "180")

        fliesPerLoveCageLb = Label(settinWin, height=1, width=8, text="#flies/LC",
                                   anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                                   font="Arial 15 bold")
        fliesPerLoveCageLb.place(x=650, y=5)

        fliesPerLoveCageTb = Entry(settinWin, width=9, font="Arial 15 bold")
        fliesPerLoveCageTb.place(x=650, y=50)
        fliesPerLoveCageTb.bind("<Button-1>", lambda e: fliesPerLoveCageKeyboard())
        fliesPerLoveCageTb.insert(0, newSettingsData[3])

        # --------------------------------------------------------------
        # Other Parameters
        # --------------------------------------------------------------
        otherParametersLB = Label(settinWin, height=1, width=20, text="Other parameters",
                                  anchor=NW,
                                  fg="Black", font="Arial 15 bold")
        otherParametersLB.place(x=5, y=100)

        # --------------------------------------------------------------
        # Number of beams/fly
        # --------------------------------------------------------------
        def noOfbeamsPerFlyKeyboard():
            global entry

            entry = noOfbeamsPerFlyTb
            keypad("350", "180")

        noOfbeamsPerFlyLb = Label(settinWin, height=1, width=15, text="No. of beams/fly",
                                  anchor=NW, fg="Black",
                                  font="Arial 15")
        noOfbeamsPerFlyLb.place(x=5, y=150)

        noOfbeamsPerFlyTb = Entry(settinWin, width=9, font="Arial 15 bold")
        noOfbeamsPerFlyTb.place(x=200, y=150)
        noOfbeamsPerFlyTb.bind("<Button-1>", lambda e: noOfbeamsPerFlyKeyboard())
        noOfbeamsPerFlyTb.insert(0, newSettingsData[4])

        # --------------------------------------------------------------
        # Dark cage shaking
        # --------------------------------------------------------------
        darkCageShakingLb = Label(settinWin, height=1, width=20, text="Dark cage shaking",
                                  anchor=NW,
                                  fg="Black", font="Arial 15 bold")
        darkCageShakingLb.place(x=5, y=200)

        # --------------------------------------------------------------
        # Dark cage shaking interval
        # --------------------------------------------------------------
        def shakingIntervalKeyboard():
            global entry

            entry = shakingIntervalTb
            keypad("350", "180")

        shakingIntervalLb = Label(settinWin, height=1, width=15, text="Interval (seconds)",
                                  anchor=NW, fg="Black",
                                  font="Arial 15")
        shakingIntervalLb.place(x=5, y=250)

        shakingIntervalTb = Entry(settinWin, width=9, font="Arial 15 bold")
        shakingIntervalTb.place(x=200, y=250)
        shakingIntervalTb.bind("<Button-1>", lambda e: shakingIntervalKeyboard())
        shakingIntervalTb.insert(0, newSettingsData[5])

        # --------------------------------------------------------------
        # Dark cage shaking duration
        # --------------------------------------------------------------
        def shakingDurationKeyboard():
            global entry

            entry = shakingDurationTb
            keypad("350", "180")

        shakingDurationLb = Label(settinWin, height=1, width=15, text="Duration (seconds)",
                                  anchor=NW, fg="Black",
                                  font="Arial 15")
        shakingDurationLb.place(x=5, y=300)

        shakingDurationTb = Entry(settinWin, width=9, font="Arial 15 bold")
        shakingDurationTb.place(x=200, y=300)
        shakingDurationTb.bind("<Button-1>", lambda e: shakingDurationKeyboard())
        shakingDurationTb.insert(0, newSettingsData[6])

        # --------------------------------------------------------------
        # Back Button
        # --------------------------------------------------------------
        def saveSettings():
            fliesPerDarkCage = fliesPerDarkCageTb.get()
            timeLimit = timeLimitTb.get()
            fliesPerTime = fliesPerTimeTb.get()
            fliesPerLoveCage = fliesPerLoveCageTb.get()
            noOfbeamsPerFly = noOfbeamsPerFlyTb.get()
            shakingInterval = shakingIntervalTb.get()
            shakingDuration = shakingDurationTb.get()

            if (
                    fliesPerDarkCage != '' and timeLimit != '' and fliesPerTime != '' and fliesPerLoveCage != '' and noOfbeamsPerFly != '' and shakingInterval != '' and shakingDuration != ''):
                settingFile = open("settings.txt", "w+")
                settingFile.write(
                    fliesPerDarkCage + '\n' + timeLimit + '\n' + fliesPerTime + '\n' + fliesPerLoveCage + '\n' + noOfbeamsPerFly + '\n' + shakingInterval + '\n' + shakingDuration)
            settinWin.destroy()

        backBtn = Button(settinWin, height=2, width=20, text="Back", font='Arial 15 bold',
                         fg="Black", bg='#75CC3D', relief=RAISED,
                         command=lambda: saveSettings())
        backBtn.place(x=250, y=350)

    def startProcess():
        global startProcessWin, newSettingsData, flyCountTb, actualtimeLimitTb, actualfliesPerTimeTb, stop

        startProcessWin = Toplevel(root)
        startProcessWin.overrideredirect(0)
        # settinWin.attributes("-toolwindow", 1)
        startProcessWin.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
        startProcessWin.resizable(0, 0)
        startProcessWin.title("Fly Counter")

        newSettingsData = []
        with open("settings.txt") as settingsFile:
            settingsData = settingsFile.readlines()

        for newline in settingsData:
            settingsData = newline.replace("\n", "")
            newSettingsData.append(settingsData)
        print(newSettingsData)

        # --------------------------------------------------------------
        # Set Value
        # --------------------------------------------------------------
        setValueLb = Label(startProcessWin, height=1, width=20, text="Set Value",
                           anchor=NW,
                           fg="Black", font="Arial 15 bold")
        setValueLb.place(x=5, y=50)

        # --------------------------------------------------------------
        # Actual Value
        # --------------------------------------------------------------
        actualValueLb = Label(startProcessWin, height=1, width=10, text="Actual Value",
                              anchor=NW,
                              fg="Black", font="Arial 15 bold")
        actualValueLb.place(x=5, y=100)

        # --------------------------------------------------------------
        # Fly Count Label
        # --------------------------------------------------------------
        flyCountLb = Label(startProcessWin, height=1, width=10, text="Fly Count",
                           anchor=NW,
                           fg="Black", font="Arial 15 bold")
        flyCountLb.place(x=5, y=275)

        # --------------------------------------------------------------
        # Fly Count Entry
        # --------------------------------------------------------------
        flyCountTb = Entry(startProcessWin, width=5, font="Arial 15 bold")
        flyCountTb.place(x=200, y=275)

        def flyCountUpdate():
            flyCountTb.delete(0, END)
            flyCountTb.insert(0, str(flyCount))

            actualfliesPerDarkCageTb.delete(0, END)
            actualfliesPerDarkCageTb.insert(0, str(flyCount))

            actualfliesPerLoveCageTb.delete(0, END)
            actualfliesPerLoveCageTb.insert(0, str(flyCount))

            if int(actualfliesPerDarkCageTb.get()) >= int(newSettingsData[0]):
                print("No. of Flies per Dark Cage are Collected")
                # stop()

            if int(actualfliesPerLoveCageTb.get()) >= int(newSettingsData[3]):
                print("No. of Flies per Love Cage are Collected")
                # stop()

            startProcessWin.after(10, flyCountUpdate)

        startProcessWin.after(10, flyCountUpdate)

        # --------------------------------------------------------------
        # LogoPhoto
        # --------------------------------------------------------------
        LogoPhotoLb = Label(startProcessWin, height=150, width=600, text="",
                            image=bgphoto)
        LogoPhotoLb.place(x=175, y=125)

        # --------------------------------------------------------------
        # Number of flies from individual dark cage
        # --------------------------------------------------------------
        fliesPerDarkCageLb = Label(startProcessWin, height=1, width=8, text="#flies/DC",
                                   anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                                   font="Arial 15 bold")
        fliesPerDarkCageLb.place(x=200, y=5)

        setfliesPerDarkCageTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        setfliesPerDarkCageTb.place(x=200, y=50)
        setfliesPerDarkCageTb.insert(0, newSettingsData[0])

        actualfliesPerDarkCageTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        actualfliesPerDarkCageTb.place(x=200, y=100)
        actualfliesPerDarkCageTb.insert(0, '0')

        # --------------------------------------------------------------
        # Time limit
        # --------------------------------------------------------------
        timeLimitLb = Label(startProcessWin, height=1, width=8, text="Time (min)",
                            anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                            font="Arial 15 bold")
        timeLimitLb.place(x=350, y=5)

        settimeLimitTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        settimeLimitTb.place(x=350, y=50)
        settimeLimitTb.insert(0, newSettingsData[1])

        actualtimeLimitTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        actualtimeLimitTb.place(x=350, y=100)
        actualtimeLimitTb.insert(0, '0')

        # --------------------------------------------------------------
        # Number of flies per time interval
        # --------------------------------------------------------------
        fliesPerTimeLb = Label(startProcessWin, height=1, width=8, text="#flies/min",
                               anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                               font="Arial 15 bold")
        fliesPerTimeLb.place(x=500, y=5)

        setfliesPerTimeTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        setfliesPerTimeTb.place(x=500, y=50)
        setfliesPerTimeTb.insert(0, newSettingsData[2])

        actualfliesPerTimeTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        actualfliesPerTimeTb.place(x=500, y=100)
        actualfliesPerTimeTb.insert(0, '0')

        # --------------------------------------------------------------
        # Total number of flies in love cage
        # --------------------------------------------------------------
        fliesPerLoveCageLb = Label(startProcessWin, height=1, width=8, text="#flies/LC",
                                   anchor=NW, fg="Black", bg='Grey', relief=RIDGE,
                                   font="Arial 15 bold")
        fliesPerLoveCageLb.place(x=650, y=5)

        setfliesPerLoveCageTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        setfliesPerLoveCageTb.place(x=650, y=50)
        setfliesPerLoveCageTb.insert(0, newSettingsData[3])

        actualfliesPerLoveCageTb = Entry(startProcessWin, width=9, font="Arial 15 bold")
        actualfliesPerLoveCageTb.place(x=650, y=100)
        actualfliesPerLoveCageTb.insert(0, '0')

        # --------------------------------------------------------------
        # Current Dark Cage
        # --------------------------------------------------------------
        currentDarkCageLb = Label(startProcessWin, height=1, width=5, text=darkCageQRcode,
                                  anchor=NW, fg="Black", bg='Yellow', relief=RIDGE,
                                  font="Arial 15 bold")
        currentDarkCageLb.place(x=300, y=275)

        # --------------------------------------------------------------
        # Current Love Cage
        # --------------------------------------------------------------
        currentLoveCageLb = Label(startProcessWin, height=1, width=5, text=loveCageQRcode,
                                  anchor=NW, fg="Black", bg='Yellow', relief=RIDGE,
                                  font="Arial 15 bold")
        currentLoveCageLb.place(x=675, y=275)

        # --------------------------------------------------------------
        # AGITATOR Button
        # --------------------------------------------------------------
        def AGITATOR():
            print("Shake Cage")
            print(newSettingsData[4])
            print(newSettingsData[5])

        agitiatorBtn = Button(startProcessWin, height=2, width=10, text="Shake\nCage", font='Arial 15 bold',
                              fg="White", bg='Black', relief=RAISED,
                              command=lambda: AGITATOR())
        agitiatorBtn.place(x=10, y=350)

        # --------------------------------------------------------------
        # Serial Data to No. of Flies
        # --------------------------------------------------------------

        # --------------------------------------------------------------
        # Start Button
        # --------------------------------------------------------------
        def start():
            global startFlag, loveCageFlag, darkCageFlag, startTime, noOfFliesPerMinTimer, flyCount

            # if loveCageFlag == 1 and darkCageFlag == 1:
            print("Start")
            startFlag = 1
            flyCount = 0
            startTime = time.time()
            print('startTime', datetime.now())
            threading.Thread(target=read_serial_packet).start()
            noOfFliesPerMinTimer = root.after(10000, noOfFliesPerMin)

            logsData[0] = str(datetime.now())[:10]
            logsData[1] = darkCageQRcode
            logsData[2] = str(datetime.now())[10:19]

            loveCageLogsFile = path + 'logs/' + loveCageQRcode + '.csv'
            if os.path.exists(loveCageLogsFile):
                with open(loveCageLogsFile, 'a', encoding='UTF8', newline='') as logs:
                    writer = csv.writer(logs)
                    writer.writerow(logsData)

            else:
                print("Creating Logs File")
                with open(loveCageLogsFile, 'w', encoding='UTF8', newline='') as logs:
                    writer = csv.writer(logs)
                    writer.writerow(logsHeader)
                    writer.writerow(logsData)

            stopBtn = Button(startProcessWin, height=2, width=10, text="Stop", font='Arial 15 bold',
                             fg="Black", bg='Red', relief=RAISED,
                             command=lambda: stop())
            stopBtn.place(x=150, y=350)

        startBtn = Button(startProcessWin, height=2, width=10, text="Start", font='Arial 15 bold',
                          fg="Black", bg='#75CC3D', relief=RAISED,
                          command=lambda: start())
        startBtn.place(x=150, y=350)

        # --------------------------------------------------------------
        # Stop Button
        # --------------------------------------------------------------
        def stop():
            global count, startFlag

            print("Stop")
            startFlag = 0
            count = 0
            if not sensor.isOpen():
                sensor.open()
            sensor.write(b'0')
            sensor.flush()
            sensor.close()
            if noOfFliesPerMinTimer!= '':
                root.after_cancel(noOfFliesPerMinTimer)

            loveCageLogsFile = path + 'logs/' + loveCageQRcode + '.csv'
            if os.path.exists(loveCageLogsFile):
                logsRead = list(csv.reader(open(loveCageLogsFile)))
                logsRead.pop()

                logsData[3] = str(datetime.now())[10:19]

                with open(loveCageLogsFile, 'w', encoding='UTF8', newline='') as logs:
                    writer = csv.writer(logs)
                    writer.writerows(logsRead)
                    writer.writerow(logsData)

            startBtn = Button(startProcessWin, height=2, width=10, text="Start", font='Arial 15 bold',
                              fg="Black", bg='#75CC3D', relief=RAISED,
                              command=lambda: start())
            startBtn.place(x=150, y=350)

        # --------------------------------------------------------------
        # Next Dark Cage Button
        # --------------------------------------------------------------
        def fillDarkCageQRscan():
            fillDarkCageQRscanWin = Toplevel(root)
            fillDarkCageQRscanWin.overrideredirect(0)
            # fillDarkCageQRscanWin.attributes("-toolwindow", 1)
            fillDarkCageQRscanWin.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
            fillDarkCageQRscanWin.resizable(0, 0)
            fillDarkCageQRscanWin.title("Fill Dark Cage QR Scan")

            # --------------------------------------------------------------
            # Scan QR-code of Dark Cage Label
            # --------------------------------------------------------------
            LogoLb = Label(fillDarkCageQRscanWin, height=1, width=25, text="Scan QR-code of Dark Cage",
                           anchor=CENTER,
                           fg="Black", font="Arial 36 bold")
            LogoLb.place(x=10, y=10)

            # --------------------------------------------------------------
            # Scan QR-code of Love Cage Status Label
            # --------------------------------------------------------------
            scanDCstatusLb = Label(fillDarkCageQRscanWin, height=10, width=40,
                                   text="Place the Camera in front of Dark Cage to\nScan QR code",
                                   anchor=CENTER, fg="Black", bg='Grey', relief=RIDGE,
                                   font="Arial 15 bold")
            scanDCstatusLb.place(x=125, y=75)

            # --------------------------------------------------------------
            # Scan Button
            # --------------------------------------------------------------
            def darkCageScanQRcode():
                global darkCageFlag, darkCageQRcode

                newDarkCageQRcodeData = []
                with open(path + 'qrCode/' + "darkCageQRcode.txt") as darkCageQRcodeFile:
                    darkCageQRcodeData = darkCageQRcodeFile.readlines()

                for newline in darkCageQRcodeData:
                    darkCageQRcodeData = newline.replace("\n", "")
                    newDarkCageQRcodeData.append(darkCageQRcodeData)
                print(newDarkCageQRcodeData)

                resp = requests.get(url, stream=True)
                local_file = open(path + 'images/' + 'local_image.jpg', 'wb')
                resp.raw.decode_content = True
                shutil.copyfileobj(resp.raw, local_file)

                # subprocess.Popen("libcamera-still -r -o /home/pi/flyCounter/local_image.jpg", shell=True)
                image = cv2.imread(path + 'images/' + 'local_image.jpg', 0)
                barcodes = pyzbar.decode(image)

                if not barcodes:
                    darkCageFlag = 0
                    darkCageQRcode = ''

                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    darkCageQRcode = barcode.data.decode("utf-8")
                    print(darkCageQRcode)

                if darkCageQRcode in newDarkCageQRcodeData:
                    darkCageFlag = 1
                    for darkCage in range(0, 4):
                        if newDarkCageQRcodeData[darkCage] == darkCageQRcode:
                            print(str(1 + darkCage))
                            scanDCstatusLb.configure(text="Dark Cage " + str(1 + darkCage) + " QR Code Detected")

                else:
                    scanDCstatusLb.configure(text="Scan QR Code Again for Dark Cage")

            scanBtn = Button(fillDarkCageQRscanWin, height=2, width=20, text="Scan QR-code", font='Arial 15 bold',
                             fg="Black", bg='#75CC3D', relief=RAISED,
                             command=lambda: darkCageScanQRcode())
            scanBtn.place(x=100, y=350)

            # --------------------------------------------------------------
            # Next Button for fillDarkCageQRscan
            # --------------------------------------------------------------
            def process():
                startProcess()
                fillDarkCageQRscanWin.destroy()

            nextBtn = Button(fillDarkCageQRscanWin, height=2, width=20, text="Next", font='Arial 15 bold',
                             fg="Black", bg='#00A3FF', relief=RAISED,
                             command=lambda: process())
            nextBtn.place(x=400, y=350)

            stop()
            startProcessWin.destroy()

        fillDarkCageBtn = Button(startProcessWin, height=2, width=10, text="Next\nDark Cage", font='Arial 15 bold',
                                 fg="Black", bg='#00A3FF', relief=RAISED,
                                 command=lambda: fillDarkCageQRscan())
        fillDarkCageBtn.place(x=300, y=350)

        # --------------------------------------------------------------
        # View Log Button
        # --------------------------------------------------------------
        def viewLog():
            viewLogWin = Toplevel(root)
            viewLogWin.overrideredirect(0)
            # viewLogWin.attributes("-toolwindow", 1)
            viewLogWin.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
            viewLogWin.resizable(0, 0)
            viewLogWin.title("View Log")

            backBtn = Button(viewLogWin, height=2, width=10, text="Back", font='Arial 15 bold',
                             fg="Black", bg='#00A3FF', relief=RAISED,
                             command=lambda: viewLogWin.destroy())
            backBtn.place(x=600, y=350)

        viewLogBtn = Button(startProcessWin, height=2, width=10, text="View Log", font='Arial 15 bold',
                            fg="Black", bg='#00A3FF', relief=RAISED,
                            command=lambda: viewLog())
        viewLogBtn.place(x=450, y=350)

        # --------------------------------------------------------------
        # End Button
        # --------------------------------------------------------------
        def end():
            stop()
            startProcessWin.destroy()

        endBtn = Button(startProcessWin, height=2, width=10, text="End", font='Arial 15 bold',
                        fg="Black", bg='#00A3FF', relief=RAISED,
                        command=lambda: end())
        endBtn.place(x=600, y=350)

    # --------------------------------------------------------------
    # LogoPhoto
    # --------------------------------------------------------------
    LogoPhotoLb = Label(root, height=200, width=600, text="",
                        image=bgphoto)
    LogoPhotoLb.place(x=50, y=100)

    # --------------------------------------------------------------
    # Black Soldier Fly Counter Label
    # --------------------------------------------------------------
    LogoLb = Label(root, height=1, width=20, text="Black Soldier Fly Counter",
                   anchor=NW,
                   fg="Black", font="Arial 48 bold")
    LogoLb.place(x=10, y=10)

    # --------------------------------------------------------------
    # Fill Love Cage Button
    # --------------------------------------------------------------
    fillLoveCageBtn = Button(root, height=2, width=20, text="Fill Love Cage", font='Arial 15 bold',
                             fg="Black", bg='#75CC3D', relief=RAISED,
                             command=lambda: fillLoveCageQRscan())
    fillLoveCageBtn.place(x=100, y=350)

    # --------------------------------------------------------------
    # Setting Button
    # --------------------------------------------------------------
    settingBtn = Button(root, height=2, width=20, text="Settings", font='Arial 15 bold',
                        fg="Black", bg='#00A3FF', relief=RAISED,
                        command=lambda: setting())
    settingBtn.place(x=400, y=350)

    # --------------------------------------------------------------
    # Logs Update
    # --------------------------------------------------------------
    def logsUpdate():
        if startFlag:
            elapsedTime = float((time.time() - startTime))
            elapsedMin = elapsedTime / 10.0

            actualtimeLimitTb.delete(0, END)
            actualtimeLimitTb.insert(0, str(int(elapsedMin)))

            actualfliesPerTimeTb.delete(0, END)
            actualfliesPerTimeTb.insert(0, str(flyCount))

            # if elapsedMin - float(newSettingsData[1]) > 0:
            #     print('elapsedTime', datetime.now())
            #     stop()

            loveCageLogsFile = path + 'logs/' + loveCageQRcode + '.csv'
            if os.path.exists(loveCageLogsFile):
                logsRead = list(csv.reader(open(loveCageLogsFile)))

                if len(logsRead) > 1:
                    logsRead.pop()

                logsData[4] = str(flyCount)
                logsData[5] = str(flyCount)

                with open(loveCageLogsFile, 'w', encoding='UTF8', newline='') as logs:
                    writer = csv.writer(logs)
                    writer.writerows(logsRead)
                    writer.writerow(logsData)

        root.after(1, logsUpdate)

    root.after(1, logsUpdate)
    root.update()
    root.mainloop()

if __name__ == "__main__":
    main()
