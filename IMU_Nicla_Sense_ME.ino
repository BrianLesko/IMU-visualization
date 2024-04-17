// Brian Lesko 
// IMU on the Arduino Nicla Sense ME

#include "Nicla_System.h"
#include "Arduino_BHY2.h"
#include <math.h>

//Raw Sensor Initialization
SensorXYZ accelerometer(SENSOR_ID_ACC);
SensorXYZ gyro(SENSOR_ID_GYRO);

//LED Initialization

//Pressure sensor Init 
Sensor pressure(SENSOR_ID_BARO);

//IMU Initialization
SensorQuaternion rotation(SENSOR_ID_RV);
SensorOrientation orientation(SENSOR_ID_ORI);  

void setup() {

  Serial.begin(115200);
  while (!Serial);
  Serial.println("Started");

  BHY2.begin();
  accelerometer.begin();
  gyro.begin();
  pressure.begin();
  rotation.begin();
  orientation.begin();

  //LED
  //nicla::begin();
  //nicla::leds.begin();
  //nicla::leds.setColor(green);

}

void loop() {
  BHY2.update();
  // Standard sea level pressure in hPa
  float P0 = 1013.25;
  Serial.println(String("Roll, Pitch, Yaw, Altitude: ") + orientation.roll() + "," + orientation.pitch() + "," + orientation.heading() + "," + (44330 * (1 - pow((pressure.value() / P0), 1/5.255))) );
  //Pressure in hPa hectopascals, conversion to altitude in meters
  //Serial.println(String("rotation: ") + rotation.toString()); //Quaternion
  unsigned long endTime = millis(); // End time of the loop
}