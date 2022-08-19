# import the necessary packages
import threading
from tkinter import *
from pyzbar import pyzbar
# import RPi.GPIO as GPIO
import cv2, requests, shutil, time, serial, subprocess, fnmatch, uuid, random, binascii, datetime

# Machine = "COM4"
Machine= "/dev/ttyUSB0"
brate = "115200"
sensor = serial.Serial(Machine, baudrate=brate, timeout=0.01)
# --------------------------------------------------------------
# --------------------------------------------------------------
# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.cleanup()
# GPIO.setup(26,#GPIO.oUT, initial = GPIO.LOW) #Sensor (I/O input)
# --------------------------------------------------------------
# --------------------------------------------------------------
loveCageQRcode = 'LC1'
darkCageQRcode = 'DC1'
startFlag = 0
loveCageFlag = 0
darkCageFlag = 0
serialCallback = 0
sec = 0

# url = "http://192.168.1.6:8080/shot.jpg"

# --------------------------------------------------------------
# Serial Data Thread
# --------------------------------------------------------------
def read_serial_packet():
    print("Started ::")
    while True:
        if startFlag:
            if not sensor.isOpen():
                sensor.open()
                sensor.write(b'B')
            if sensor.inWaiting() > 6:
                sensorData = sensor.read(7)
                print("Time: ", datetime.datetime.now(), "Sensor: ", sensorData)

                # seventhByte = int(binascii.hexlify(sensorData)[0:2], 16)
                # sixthByte = int(binascii.hexlify(sensorData)[2:4], 16)
                # fifthByte = int(binascii.hexlify(sensorData)[4:6], 16)
                # fourthByte = int(binascii.hexlify(sensorData)[6:8], 16)
                # thirdByte = int(binascii.hexlify(sensorData)[8:10], 16)
                # secondByte = int(binascii.hexlify(sensorData)[10:12], 16)
                # firstByte = int(binascii.hexlify(sensorData)[12:14], 16)
                #
                # print("Time: ", datetime.datetime.now(), "Sensor: ", firstByte, secondByte, thirdByte, fourthByte, fifthByte, sixthByte, seventhByte)
                # if (seventhByte >= 128 and seventhByte <= 191) and (sixthByte >= 0 and sixthByte <= 127) and (fifthByte >= 0 and fifthByte <= 127) and (fourthByte >= 0 and fourthByte <= 127) and (thirdByte >= 0 and thirdByte <= 127) and (secondByte >= 0 and secondByte <= 127) and (firstByte >= 0 and firstByte <= 127):
                #     print("Perfect Stream" )

        else:
            break

def main():
    global root

    root = Tk()
    root.overrideredirect(0)
    root.wm_geometry("800x480+0+0")  # x,y+origin x+ origin y
    root.resizable(0, 0)
    root.title("Swiss Federal Institute of Aquatic Science and Technology")
    # resp = requests.get(url, stream=True)

    # --------------------------------------------------------------
    # Images
    # --------------------------------------------------------------
    Logophoto = PhotoImage(file="images/#eawag.gif")
    bgphoto = PhotoImage(file="images/bg.gif")

    def flyCount(dividend):
        if (dividend % 3) == 0:
            return 1
        else:
            return 0

    def keypad(x, y):
        global root
        global entry
        top = Toplevel(root, relief="groove", bd=4)
        top.overrideredirect(1)
        top.wm_geometry('120x180+' + x + '+' + y)  # x,y+origin x+ origin y

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
        global scanLCstatusLb
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

            loveCageQRcode = ''
            newLoveCageQRcodeData = []
            with open("loveCageQRcode.txt") as loveCageQRcodeFile:
                loveCageQRcodeData = loveCageQRcodeFile.readlines()

            for newline in loveCageQRcodeData:
                loveCageQRcodeData = newline.replace("\n", "")
                newLoveCageQRcodeData.append(loveCageQRcodeData)
            print(newLoveCageQRcodeData)

            # resp = requests.get(url, stream=True)
            # local_file = open('local_image.jpg', 'wb')
            # resp.raw.decode_content = True
            # shutil.copyfileobj(resp.raw, local_file)

            subprocess.call("raspstill -vf -o /home/pi/flyCounter/local_image.jpeg", shell=True)
            image = cv2.imread('local_image.jpg', 0)
            barcodes = pyzbar.decode(image)

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
        # Time Interval
        # --------------------------------------------------------------
        # def timeIntervalKeyboard():
        #     global entry
        #     
        #     entry = timeIntervalTb
        #     keypad("350", "180")
        #
        # timeIntervalLb = Label(settinWin, height=2, width=20, text="Time Interval\n(Seconds)", anchor=NW,
        #                        font="Arial 10 bold")
        # timeIntervalLb.place(x=10, y=300)
        #
        # timeIntervalTb = Entry(settinWin, width=10, font='13')
        # timeIntervalTb.place(x=160, y=300)
        # timeIntervalTb.bind("<Button-1>", lambda e: timeIntervalKeyboard())
        # timeIntervalTb.insert(0, '100')  

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
        def noOfBeamsPerFlyKeyboard():
            global entry

            entry = noOfBeamsPerFlyTb
            keypad("350", "180")

        noOfBeamsPerFlyLb = Label(settinWin, height=1, width=15, text="No. of beams/fly",
                                  anchor=NW, fg="Black",
                                  font="Arial 15")
        noOfBeamsPerFlyLb.place(x=5, y=150)

        noOfBeamsPerFlyTb = Entry(settinWin, width=9, font="Arial 15 bold")
        noOfBeamsPerFlyTb.place(x=200, y=150)
        noOfBeamsPerFlyTb.bind("<Button-1>", lambda e: noOfBeamsPerFlyKeyboard())
        noOfBeamsPerFlyTb.insert(0, newSettingsData[4])

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
            noOfBeamsPerFly = noOfBeamsPerFlyTb.get()
            shakingInterval = shakingIntervalTb.get()
            shakingDuration = shakingDurationTb.get()

            if (
                    fliesPerDarkCage != '' and timeLimit != '' and fliesPerTime != '' and fliesPerLoveCage != '' and noOfBeamsPerFly != '' and shakingInterval != '' and shakingDuration != ''):
                settingFile = open("settings.txt", "w+")
                settingFile.write(
                    fliesPerDarkCage + '\n' + timeLimit + '\n' + fliesPerTime + '\n' + fliesPerLoveCage + '\n' + noOfBeamsPerFly + '\n' + shakingInterval + '\n' + shakingDuration)
                settingFile.close
            settinWin.destroy()

        backBtn = Button(settinWin, height=2, width=20, text="Back", font='Arial 15 bold',
                         fg="Black", bg='#75CC3D', relief=RAISED,
                         command=lambda: saveSettings())
        backBtn.place(x=250, y=350)

    def startProcess():
        global startProcessWin

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
            global startFlag
            print("Start")
            startFlag = 1
            threading.Thread(target=read_serial_packet).start()

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
            global serialCallback, startFlag
            startFlag = 0
            if not sensor.isOpen():
                sensor.open()
                sensor.write(b'0')
                sensor.close()
            print("Stop")

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

                darkCageQRcode = ''
                newDarkCageQRcodeData = []
                with open("darkCageQRcode.txt") as darkCageQRcodeFile:
                    darkCageQRcodeData = darkCageQRcodeFile.readlines()

                for newline in darkCageQRcodeData:
                    darkCageQRcodeData = newline.replace("\n", "")
                    newDarkCageQRcodeData.append(darkCageQRcodeData)
                print(newDarkCageQRcodeData)

                # resp = requests.get(url, stream=True)
                # local_file = open('local_image.jpg', 'wb')
                # resp.raw.decode_content = True
                # shutil.copyfileobj(resp.raw, local_file)

                subprocess.call("raspstill -vf -o /home/pi/flyCounter/local_image.jpeg", shell=True)
                image = cv2.imread('local_image.jpg', 0)
                barcodes = pyzbar.decode(image)

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

    root.update()
    root.mainloop()


if __name__ == "__main__":
    main()
