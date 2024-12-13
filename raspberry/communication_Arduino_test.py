import io, socket, struct, time, picamera, serial, mysql.connector
from threading import Thread


class Manual:
    def __init__(self, End, serial):
        Msg = input("Manual mode input(start + data+ end) : ")
        Start = Msg[:3]
        Msg = Msg[3:-1]

        if Start == "GRA":
            SendStart = b"RAA"
            SendPacket = SendStart + End
            serial.write(SendPacket)
        
        elif Msg == "GRM":
            data = Msg[0]
            checksum = Msg[-1]
            check = format(int.from_bytes(data, byteorder="big"), '#x') + format(int.from_bytes(checksum, byteorder="big"), '#x')
            checks = check & 0xff
            
            if checks == 0x00:
                SendStart = b'RAM'
                checksum = data & 0xFF
                checksum = (~checksum & 0xFF) + 1
                SendPacket = SendStart + data + checksum + End
                serial.write(SendPacket)



class DataUpload:
    def __init__(self, End, serial):
        while True:
            msg = b''

            while End not in msg:
                msg += serial.read()

            print("receive:", msg)

            if msg != b'':
                start = msg[:3]
                print(start)

                if start == b'ARA' and len(msg) == 26:
                    start = start.decode()
                    msg = msg[3:-len(End)]
                    print("cut start, end:", msg)

                    if start == "ARA":
                        control = msg[0].to_bytes(1, byteorder = 'big').decode()
                        print(control)
                        sound_check = msg[1]
                        # print(sound_check)
                        sound = msg[2:14]
                        ultra_check = msg[14]
                        # print(ultra_check)
                        ultra = msg[15:19]
                        motor_check = msg[19]
                        # print(motor_check)
                        motor = msg[20:21]
                        checksum = msg[-1].to_bytes(1, byteorder = 'big')
                        # print(checksum)
                        if sound_check.to_bytes(1, byteorder = 'big').decode() == 'S' and ultra_check.to_bytes(1, byteorder = 'big').decode() == 'U' and motor_check.to_bytes(1, byteorder = 'big').decode() == 'M':
                            checksum_check = 0

                            for i in [sound, ultra, motor, checksum]:
                                for j in i:
                                    checksum_check += j
                            # for i in msg:
                            #     checksum_check += i

                            print("checksum:", checksum)
                            print("checksum_check:", checksum_check)
                            print("checksum_check byte:", checksum_check.to_bytes(2, byteorder="big"))
                            checksum_check &= 0xFF
                            print("checksum_check cal:", checksum_check)
                            # checksum_check = checksum_check.to_bytes(1, byteorder="big")
                            # print(checksum_check)

                            if checksum_check == 0x00:
                                sound1 = msg[2:6]
                                sound2 = msg[6:10]
                                sound3 = msg[10:14]
                                sound1_de = int.from_bytes(sound1, byteorder="big")
                                sound2_de = int.from_bytes(sound2, byteorder="big")
                                sound3_de = int.from_bytes(sound3, byteorder="big")
                                print("sound1:", sound1_de/10000, "sound2:", sound2_de/10000, "sound3:", sound3_de/10000)
                                ultra1 = msg[15:17]
                                ultra2 = msg[17:19]
                                ultra2_de = int.from_bytes(ultra2, byteorder="big")
                                ultra1_de = int.from_bytes(ultra1, byteorder="big")
                                print("ultra1:",ultra1_de, "ultra2:", ultra2_de)
                                motor = msg[20:21]
                                print("motor:", motor)

                                checksum = msg[-1]
                                print("checksum:", checksum, type(checksum))                



if __name__ == "__main__":
    EndMarker = b'\n'
    ArduinoSerial = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

    # manual_thread = Thread(target=lambda: Manual(EndMarker, ArduinoSerial))
    dataUpload_thread = Thread(target=lambda: DataUpload(EndMarker, ArduinoSerial))
    # manual_thread.start()
    dataUpload_thread.start()