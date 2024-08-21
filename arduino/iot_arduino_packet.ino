#include <NewPing.h>

// 소리 센서 핀 및 설정
const int soundSensor1Pin = A0;
const int soundSensor2Pin = A1;
const int soundSensor3Pin = A2;

// 초음파 센서 핀 설정
const int triggerPin1 = 7; 
const int echoPin1 = 8;     
const int triggerPin2 = 9;  
const int echoPin2 = 10;   
const int maxDistance = 40; // 초음파 센서의 최대 거리(cm)

NewPing sonar1(triggerPin1, echoPin1, maxDistance);
NewPing sonar2(triggerPin2, echoPin2, maxDistance); // correction

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

// 2차적 필터: 상보 필터 적용
float applyComplementaryFilter(int raw_value, float &filter_state) 
{
    // 매트랩으로 계산된 필터 계수
    float A = 0.8182;
    float B = 0.0091;
    float C = 1;
    float D = 0;

    // 주파수 영역 -> 시간 영역으로 변환(상태 방정식)
    float x = filter_state;
    float y = C * x + D * raw_value;
    filter_state = A * x + B * raw_value;
    
    return y;
}

void setup() 
{
    Serial.begin(115200);

    // 소리 센서 핀 설정
    pinMode(soundSensor1Pin, INPUT);
    pinMode(soundSensor2Pin, INPUT);
    pinMode(soundSensor3Pin, INPUT);

    // 초음파 센서 핀 설정
    pinMode(triggerPin1, OUTPUT);
    pinMode(echoPin1, INPUT);
    pinMode(triggerPin2, OUTPUT);
    pinMode(echoPin2, INPUT);

    // 모터 핀 설정
    pinMode(motorPin, INPUT);

    // 샘플링 주기 타이머 초기화
    t_start = millis();
}

void loop() 
{
    // 주기적 샘플링 - 0.02초(20ms) 주기
    if (millis() - t_start >= 20) 
    {
        t_start = millis(); // 주기 타이머 초기화

        // 소리 신호의 오프셋을 먼저 제거(1차 필터)
        int raw_sound1 = analogRead(soundSensor1Pin) - sound1_offset;
        int raw_sound2 = analogRead(soundSensor2Pin) - sound2_offset;
        int raw_sound3 = analogRead(soundSensor3Pin) - sound3_offset;

        // 상보 필터 적용(2차 필터)
        filtered_sound1 = applyComplementaryFilter(raw_sound1, sound1_filter_state);
        filtered_sound2 = applyComplementaryFilter(raw_sound2, sound2_filter_state);
        filtered_sound3 = applyComplementaryFilter(raw_sound3, sound3_filter_state);

        // 초음파 센서로부터 거리값 읽기
        int distance1 = sonar1.ping_cm();
        int distance2 = sonar2.ping_cm();

        // 모터값 읽기
        int motorValue = analogRead(motorPin);
        
        // 데이터를 프로토콜에 맞게 패킷화하여 전송
        sendPacket(filtered_sound1, filtered_sound2, filtered_sound3, distance1, distance2, motorValue);
    }
}

// 데이터 패킷을 전송하는 함수
void sendPacket(float sound1, float sound2, float sound3, int distance1, int distance2, int motorValue) 
{ 
    // check sum 초기화
    uint8_t checksum = 0;  

    // 패킷의 시작 부분 전송 (A R A)
    Serial.print('A');
    Serial.print('R');
    Serial.print('A');

    // 소리 센서 데이터 전송 (S로 시작)
    Serial.print('S');
    checksum += sendSensorData(sound1);
    checksum += sendSensorData(sound2);
    checksum += sendSensorData(sound3);
    
    // 초음파 센서 데이터 전송 (U로 시작)
    Serial.print('U');
    checksum += sendSensorData((float)distance1);
    checksum += sendSensorData((float)distance2);

    // 모터 값 전송 (M으로 시작)
    Serial.print('M');
    checksum += sendSensorData((float)motorValue);

    // 캐리 니블을 버리고 2의 보수 취하기
    checksum = calculateChecksum(checksum);
    Serial.write(checksum);

    // end 시퀀스 전송 (패킷의 끝)
    Serial.write('\n');
}

// 센서 데이터를 8바이트로 변환하고 상위 4바이트와 하위 4바이트로 분할하여 전송하는 함수
uint8_t sendSensorData(float value) 
{
    // 8바이트(64비트)로 변환
    uint64_t data;
    memcpy(&data, &value, sizeof(data));  // float을 uint64_t로 변환

    // 상위 4바이트 추출 및 전송
    uint32_t upper_data = (data >> 32) & 0xFFFFFFFF;
    Serial.write((uint8_t*)&upper_data, sizeof(upper_data));

    // 하위 4바이트 추출 및 전송
    uint32_t lower_data = data & 0xFFFFFFFF;
    Serial.write((uint8_t*)&lower_data, sizeof(lower_data));

    // check sum 계산
    uint8_t checksum = 0;
    checksum += upper_data & 0xFF;
    checksum += (upper_data >> 8) & 0xFF;
    checksum += (upper_data >> 16) & 0xFF;
    checksum += (upper_data >> 24) & 0xFF;
    checksum += lower_data & 0xFF;
    checksum += (lower_data >> 8) & 0xFF;
    checksum += (lower_data >> 16) & 0xFF;
    checksum += (lower_data >> 24) & 0xFF;

    return checksum;
}

// check sum 계산
uint8_t calculateChecksum(uint8_t checksum) 
{
    // 캐리 니블 버리기: 하위 8비트만 남기기
    checksum = checksum & 0xFF;

    // 2의 보수 취하기
    checksum = ~checksum + 1;

    return checksum;
}