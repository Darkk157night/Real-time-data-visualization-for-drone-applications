#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ArduinoJson.h> // Include ArduinoJson library

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(9600);
  
  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  // Set up the accelerometer range
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  
  // Set up the gyroscope range
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  
  // Set filter bandwidth
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Create a JSON document
  StaticJsonDocument<256> doc;

  // Add gyroscope data
  JsonObject gyro = doc.createNestedObject("gyro");
  gyro["x"] = g.gyro.x;
  gyro["y"] = g.gyro.y;
  gyro["z"] = g.gyro.z;


  // Serialize the JSON document and send it to Serial
  serializeJson(doc, Serial);
  Serial.println();  // Print a newline for better readability

  delay(100);
}
