#include <NewPing.h>

// 소리 센서 핀 설정
const int soundSensor1Pin = A0;
const int soundSensor2Pin = A1;
const int soundSensor3Pin = A2;

// 초음파 센서 핀 설정
const int triggerPin1 = 4; 
const int echoPin1 = 8;     
const int triggerPin2 = 9;  
const int echoPin2 = 10;   
const int maxDistance = 40; // 초음파 센서의 최대 거리(cm)

NewPing sonar1(triggerPin1, echoPin1, maxDistance);
NewPing sonar2(triggerPin2, echoPin2, maxDistance); 

// 모터 핀 설정
const int motorPin = 3;

// 오프셋 저장 변수
const float sound1_offset = 31.2495;
const float sound2_offset = 31.5667;
const float sound3_offset = 31.5102;

// 필터링된 값 저장 변수
float filtered_sound1 = 0;
float filtered_sound2 = 0;
float filtered_sound3 = 0;

// 상보 필터 상태 변수
float sound1_filter_state = 0;
float sound2_filter_state = 0;
float sound3_filter_state = 0;

unsigned long t_start = 0;

//********** Function declaration code **********//

// 2차적 필터: 상보 필터 적용
float applyComplementaryFilter(int raw_value, float &filter_state) 
{
    float A = 0.9933555;
    float B = 0.0199335;
    float C = 1;
    float D = 0;

    float x = filter_state;
    float y = C * x + D * raw_value;
    filter_state = A * x + B * raw_value;
    
    return y;
}

// 패킷으로 데이터를 전송하는 함수
void sendPacket(char sensorType, float sound1, float sound2, float sound3, int distance1, int distance2, uint8_t motorValue) 
{   
    uint8_t packet[29]; // 패킷을 위한 배열 (ARA + 타입 + 센서 데이터 + 체크섬 + '\n' 포함)
    uint8_t checksum = 0;

    // 패킷 시작 ('ARA')
    packet[0] = 'A';
    packet[1] = 'R';
    packet[2] = 'A';

    // 센서 타입 ('S' 또는 'U')
    packet[3] = sensorType;

    // 소리 센서 데이터 시작 ('S')
    packet[4] = 'S';

    // 소리 센서 데이터를 고정 소수점으로 변환하여 패킷에 추가
    uint32_t sound1_fixed = convertToFixedPoint(sound1);
    uint32_t sound2_fixed = convertToFixedPoint(sound2);
    uint32_t sound3_fixed = convertToFixedPoint(sound3);
    
    packet[5] = (sound1_fixed >> 24) & 0xFF;
    packet[6] = (sound1_fixed >> 16) & 0xFF;
    packet[7] = (sound1_fixed >> 8) & 0xFF;
    packet[8] = sound1_fixed & 0xFF;

    packet[9] = (sound2_fixed >> 24) & 0xFF;
    packet[10] = (sound2_fixed >> 16) & 0xFF;
    packet[11] = (sound2_fixed >> 8) & 0xFF;
    packet[12] = sound2_fixed & 0xFF;

    packet[13] = (sound3_fixed >> 24) & 0xFF;
    packet[14] = (sound3_fixed >> 16) & 0xFF;
    packet[15] = (sound3_fixed >> 8) & 0xFF;
    packet[16] = sound3_fixed & 0xFF;

    // 초음파 센서 데이터 시작 ('U')
    packet[17] = 'U';
    packet[18] = (distance1 >> 8) & 0xFF;  // distance1의 상위 1바이트
    packet[19] = distance1 & 0xFF;         // distance1의 하위 1바이트
    packet[20] = (distance2 >> 8) & 0xFF;  // distance2의 상위 1바이트
    packet[21] = distance2 & 0xFF;         // distance2의 하위 1바이트

    // 모터 데이터 시작 ('M')
    packet[22] = 'M';
    packet[23] = motorValue;

    checksum = packet[5]+packet[6]+packet[7]+packet[8]+packet[9]+packet[10]+packet[11]+packet[12]+packet[13]+packet[14]+packet[15]+packet[16]+packet[18]+packet[19]+packet[20]+packet[21]+packet[23];

    checksum = sensor_calculateChecksum(checksum);
    packet[24] = checksum;

    // 패킷 끝에 '\n' 추가
    packet[25] = '\n';

    // 패킷 전송
    Serial.write(packet, 26); // 26바이트 패킷 전송 (\n 포함)
}

// 소리센서 값을 고정 소수점으로 변환하는 함수
uint32_t convertToFixedPoint(float value) 
{
    return (uint32_t)(value * 10000); // 소수점 4자리까지 고정 소수점으로 변환
}

// sensor check sum 계산 함수
uint8_t sensor_calculateChecksum(uint8_t checksum) 
{   
    checksum = checksum & 0xFF;
    checksum = ~checksum + 1;

    return checksum;
}

// 라즈베리파이로부터 받은 데이터를 처리하는 함수
void processReceivedData() 
{
    if (Serial.available() >= 6) 
    {
        // 6바이트 데이터를 순차적으로 읽어들임 (RAA 또는 RAM + 1바이트 데이터 + 1바이트 체크섬 + \n)
        char byte1 = Serial.read();
        char byte2 = Serial.read();
        char byte3 = Serial.read();
        uint8_t motorValue = Serial.read();
        uint8_t receivedChecksum = Serial.read();
        char endChar = Serial.read();

        // 마지막 바이트가 '\n'인지 확인, 아니라면 무시
        if (endChar != '\n') 
        {
            return;
        }

        // 받은 명령어를 문자열로 변환
        String receivedCommand = String(byte1) + String(byte2) + String(byte3);

        if (receivedCommand.equals("RAA")) 
        {
            // 아두이노가 자체적으로 모터를 제어
            analogWrite(motorPin, 0);  // 예시: 모터를 중지
        } 
        else if (receivedCommand.equals("RAM")) 
        {
            // 체크섬 계산(모터 값과 받은 체크섬을 더한 후 하위 8비트가 0x00이어야 함)
            uint16_t sum = motorValue + receivedChecksum;
            uint8_t calculatedChecksum = sum & 0xFF;

            if (calculatedChecksum == 0x00) 
            {
                // 체크섬이 일치하면 모터 제어
                int adjustedMotorValue = constrain(motorValue, 20, 160);
                analogWrite(motorPin, adjustedMotorValue);
            } 
            else 
            {
                // 체크섬이 일치하지 않으면 데이터를 무시하고 다음 데이터를 기다림
                return;
            }
        }
    }
}

//********** Main code **********//
void setup() 
{
    Serial.begin(115200);

    pinMode(soundSensor1Pin, INPUT);
    pinMode(soundSensor2Pin, INPUT);
    pinMode(soundSensor3Pin, INPUT);

    pinMode(triggerPin1, OUTPUT);
    pinMode(echoPin1, INPUT);
    pinMode(triggerPin2, OUTPUT);
    pinMode(echoPin2, INPUT);

    pinMode(motorPin, OUTPUT);

    t_start = millis();
}

void loop() 
{
    if (millis() - t_start >= 20) 
    {
        t_start = millis(); 

        int raw_sound1 = analogRead(soundSensor1Pin) - sound1_offset;
        int raw_sound2 = analogRead(soundSensor2Pin) - sound2_offset;
        int raw_sound3 = analogRead(soundSensor3Pin) - sound3_offset;

        filtered_sound1 = applyComplementaryFilter(raw_sound1, sound1_filter_state);
        filtered_sound2 = applyComplementaryFilter(raw_sound2, sound2_filter_state);
        filtered_sound3 = applyComplementaryFilter(raw_sound3, sound3_filter_state);

        int distance1 = sonar1.ping_cm();
        int distance2 = sonar2.ping_cm();

        // 소리센서 값이 기준에 따라 패킷 타입 결정
        char sensorType = (filtered_sound1 <= 10 && filtered_sound2 <= 10 && filtered_sound3 <= 10) ? 'U' : 'S';

        sendPacket(sensorType, filtered_sound1, filtered_sound2, filtered_sound3, distance1, distance2, analogRead(motorPin));
        
        // 라즈베리파이로부터 데이터 읽기
        processReceivedData();
    }
}