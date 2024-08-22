#include <NewPing.h>

// 소리 센서 핀 및 설정
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
//const int motorPin = 3; 

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

// 2차적 필터: 상보 필터 적용
float applyComplementaryFilter(int raw_value, float &filter_state) 
{
    float A = 0.8182;
    float B = 0.0091;
    float C = 1;
    float D = 0;

    float x = filter_state;
    float y = C * x + D * raw_value;
    filter_state = A * x + B * raw_value;
    
    return y;
}

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

    //pinMode(motorPin, INPUT);

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

        sendPacket(filtered_sound1, filtered_sound2, filtered_sound3, distance1, distance2);
    }
}

void sendPacket(float sound1, float sound2, float sound3, int distance1, int distance2) 
{   
    uint8_t checksum = 0;  

    Serial.print('A');
    Serial.print('R');
    Serial.print('A');

    Serial.print('S');
    checksum += sendSensorData((uint16_t)sound1, checksum);
    checksum += sendSensorData((uint16_t)sound2, checksum);
    checksum += sendSensorData((uint16_t)sound3, checksum);
    
    Serial.print('U');
    checksum += sendSensorData((uint16_t)distance1, checksum);
    checksum += sendSensorData((uint16_t)distance2, checksum);

    checksum = calculateChecksum(checksum);
    printBinary(checksum);  // check sum 2진수로 출력

    Serial.print('\n');
}

// 센서 데이터를 2바이트로 변환하고 상위 1바이트와 하위 1바이트로 분할하여 전송하는 함수
uint8_t sendSensorData(uint16_t value, uint8_t &checksum) 
{
    uint8_t upper_byte = (value >> 8) & 0xFF;
    uint8_t lower_byte = value & 0xFF;

    printBinary(upper_byte);  // 상위 바이트를 2진수로 출력
    printBinary(lower_byte);  // 하위 바이트를 2진수로 출력

    checksum += upper_byte;
    checksum += lower_byte;

    return checksum;
}

// check sum 계산
uint8_t calculateChecksum(uint8_t checksum) 
{   
    checksum = checksum & 0xFF;
    checksum = ~checksum + 1;

    return checksum;
}

// 8비트 2진수를 출력하는 함수 (0 패딩 포함)
void printBinary(uint8_t value) 
{
    for (int i = 7; i >= 0; i--) 
    {
        Serial.print((value >> i) & 1);
    }
    Serial.print(" ");
}