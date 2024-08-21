import io, socket, struct, time, picamera, serial, mysql.connector
from threading import Thread


class Manual:
    def __init__(self, End, serial):
        Msg = input("Manual mode input(start + data+ end) : ")
        Start = Msg[:3]

        if Start == "GRA":
            SendStart = b"RAA"
            SendPacket = SendStart + End
            serial.write(SendPacket)
        elif Msg == "GRM":
            Data = Msg[:-1]
            Data = Data.encode()
            SendStart = b'RAM'
            checksum = Data & 0xFF
            checksum = (~checksum & 0xFF) + 1
            SendPacket = SendStart + Data + checksum + End
            serial.write(SendPacket)



class DataUpload:
    def __init__(self, End, serial):
        msg = b''

        while End not in msg:
            msg += serial.readline()
        
        if msg != b'':
            start = msg[:3].decode()
            msg = msg[3:-len(End)]

            if start == "ARA":
                control = msg[0]
                sound = msg[1:7]
                ultra = msg[8:12]
                motor = msg[13:14]
                checksum = msg[-1]
                checksum_cal = sum(sound) + sum(ultra) + sum(motor) + checksum
                checksum_cal &= 0xFF

                print("sound:", sound.decode(), "ultra:", ultra.decode(), "motor:", motor.decode())
                



if __name__ == "__main__":
    EndMarker = b'\n'
    ArduinoSerial = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

    manual_thread = Thread(target=Manual(EndMarker, ArduinoSerial))
    dataUpload_thread = Thread(target=DataUpload(EndMarker, ArduinoSerial))
    manual_thread.start()
    dataUpload_thread.start()