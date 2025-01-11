# iot-repo-6
IoT 프로젝트 2조 저장소. 스마트 CCTV 시스템


### 🏁 1. 주제 
---
<img src="https://github.com/user-attachments/assets/e42fc367-a340-4e99-bb4f-3f55bb376bb1" width="500" height="300"> 

<br/><br/>
집 내부의 소리를 위치추정 기반으로 CCTV 카메라를 사용하여 일반 가정집의 보안 시스템을 구축하기 위함.


### 👨‍👨‍👦 2. 팀원 소개 및 역할
---

|이름 | 맡은 역할 |
|:-----------:|--------------------------------------------|
|**이재훈(팀장)**| &#8226; DB 구조 설계 및 구현 <br> &#8226; GUI <-> RPI <-> Arduino 통신 설계 및 구현 <br> &#8226; HardWare 제작 |
|**이시원**| &#8226; HW 구성도 설계 <br> &#8226; TDOA 소리 위치 추정 알고리즘 설계 및 구현 <br> &#8226; Hardware 구성 및 제작 |
|**김제백**| &#8226; SW / HW 구성도 설계 <br> &#8226; GUI 설계 및 구현 <br> &#8226; Hardware 제작 |

### ⚙ 3. 기술 스택 
---

|분류| 사용기술|
|-----|-----------------------------------------------------------|
|사용 언어| <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"> &nbsp; <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white"> &nbsp; <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white"> | 
|개발 환경     | <img src="https://img.shields.io/badge/RASPBERRY PI-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white"> &nbsp; <img src="https://img.shields.io/badge/ARDUINO-00878F?style=for-the-badge&logo=arduino&logoColor=white">  <img src="https://img.shields.io/badge/PYQT5-83B81A?style=for-the-badge&logo=pyqt5&logoColor=white">     |
|영상 처리     | <img src="https://img.shields.io/badge/OPENCV-A22846?style=for-the-badge&logo=opencv&logoColor=white"> |
|협업 툴     | <img src="https://img.shields.io/badge/SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white"> &nbsp; <img src="https://img.shields.io/badge/DISCORD-5865F2?style=for-the-badge&logo=discord&logoColor=white">                  |

### 🛠 4. 설계 
---

#### 📌 4.1 기능 리스트 

 <img src="https://github.com/user-attachments/assets/d444690a-f4e6-40ec-833c-e33b15fe1b54" width5="600" height="600">  <br/><br/>

#### 📌 4.2 HW 아키텍쳐  

 <img src="https://github.com/user-attachments/assets/22a1bc53-93f6-4b57-b8b7-a514a00504d4" width5="600" height="350">  <br/><br/>

#### 📌 4.3 SW 아키텍쳐  

  <img src="https://github.com/user-attachments/assets/1ea0912f-e838-4edc-9945-ed3799042a58" width5="1200" height="450"> <br/><br/>

#### 📌 4.4 통신 프로토콜 
   1) Arduino -> Raspberry Pi
      <br/>
      <table>
        <tr>
          <th colspan="15" align="center"> Data Packet </th>
        </tr>
        <tr>
          <th align="center" >Sensor ID</th> <th align="center">Data1_H</th> <th align="center">Data1_L</th> <th align="center">Data2_H</th> <th align="center">Data2_L</th> <th align="center">Data3_H</th> <th align="center">Data3_L</th> <th align="center">Sensor ID</th> <th align="center">Data1</th> <th align="center">Data2</th> <th align="center">Motor</th> <th align= "center">Data1</th> <th align="center" >CheckSum</th> <th align="center" > End</th>
        </tr>
        <tr>
         <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td>
        </tr>
        <tr>
         <td align="center">S</td> <td colspan="2" align = "center">SoundSensor1 Upper/Lower Value</td> <td colspan="2" align = "center">SoundSensor2 Upper/Lower Value</td> <td colspan="2" align = "center">SoundSensor3 Upper/Lower Value</td> <td align="center">U</td> <td align="center">U_Sensor1 Value</td> <td align="center">U_Sensor2 Value</td> <td align="center">M</td>
         <td align="center">Motor Value</td> <td align="center">CheckSum Value</td> <td align="center">\n</td>
        </tr>
       
      </table>  

      ( S: Sound Sensor / U: UltraSonic Sensor / M: Servo Motor )
      <br/>
      
   2) GUI -> RaspberryPi 
      <br/>
      <table>
       
       <tr>
         <th colspan="6" align="center">Data Packet</th>
       </tr>
       <tr>
         <th align="center"> Sender </th> <th align="center"> Receiver </th> <th align="center">Auto/Manual</th> <th align="center">Data1</th> <th align="center">CheckSum</th> <th align="center"> End </th>
       </tr>
       <tr>
         <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td>
       </tr>
       <tr>
         <td align="center">G</td> <td align="center">R</td> <td align="center">A</td> <td align="center">-</td> <td align="center">-</td> <td align="center">\n</td>
       </tr>
       <tr>
         <td align="center">G</td> <td align="center">R</td> <td align="center">M</td> <td align="center">Motor Value</td> <td align="center">CheckSum Value</td> <td align="center">\n</td>
       </tr>
      
      </table>

   3) Raspberry Pi -> Arduino
      <br/>
      <table>
       
       <tr>
         <th colspan="6" align="center">Data Packet</th>
       </tr>
       <tr>
         <th align="center"> Sender </th> <th align="center"> Receiver </th> <th align="center">Auto/Manual</th> <th align="center">Data1</th> <th align="center">CheckSum</th> <th align="center"> End </th>
       </tr>
       <tr>
         <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td> <td align = "center">1 Byte</td>
       </tr>
       <tr>
         <td align="center">R</td> <td align="center">A</td> <td align="center">A</td> <td align="center">-</td> <td align="center">-</td> <td align="center">\n</td>
       </tr>
       <tr>
         <td align="center">R</td> <td align="center">A</td> <td align="center">M</td> <td align="center">Motor Value</td> <td align="center">CheckSum Value</td> <td align="center">\n</td>
       </tr>
      
      </table>
      
      ( G: GUI / R: Raspberry Pi / A: Arduino / A: Auto Mode  / M: Manual Mode )
      <br/>
      
#### 📌 4.4 UI  

  <img src="https://github.com/user-attachments/assets/fecc19be-c28e-4e09-931e-9f954458922c" width5="150" height="600"> <br/><br/>
  
 
### 🎬 5. 시연 영상
---

#### 📌 5.1 라즈베리파이 <-> GUI 통신
  <img src="https://github.com/user-attachments/assets/84d1bdaf-fae8-45cd-96b4-ac2002147884" width5="150" height="400"> <br/><br/>

#### 📌 5.2 수동 모드에서 GUI 동작 
  <img src="https://github.com/user-attachments/assets/4b97377b-4b8d-4e97-87f6-7725e968b0df" width5="150" height="400"> <br/><br/>

#### 📌 5.3 TDOA 방식을 통한 위치 추정 
  <img src="https://github.com/user-attachments/assets/26745707-2940-415e-8605-7aa1d68b0b2f" width5="350" height="400"> <br/><br/>

