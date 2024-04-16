// Brian Lesko 
// IMU on the Arduino BLE Sense Rev2

#include "Arduino_BMI270_BMM150.h"
#include <Arduino_LPS22HB.h>
#include <math.h>

struct Vector3D {
    float x, y, z;

    // Overload unary minus operator
    Vector3D operator-() const {
        return Vector3D{-x, -y, -z};
    }
};

float gyro_offX, gyro_offY, gyro_offZ;
float mag_offX, mag_offY, mag_offZ;
float acc_offX, acc_offY, acc_offZ;

void calculateAllOffsets() {
  int numReadings = 500;
  float sumGyroX = 0, sumGyroY = 0, sumGyroZ = 0;
  float sumMagX = 0, sumMagY = 0, sumMagZ = 0;
  float sumAccX = 0, sumAccY = 0, sumAccZ = 0;

  for (int i = 0; i < numReadings; i++) {
    if (IMU.gyroscopeAvailable()) {
      float x, y, z;
      IMU.readGyroscope(x, y, z);
      if (abs(x) > 0.1) {
        sumGyroX += x;
      }
      if (abs(y) > 0.1) {
        sumGyroY += y;
      }
      if (abs(z) > 0.1) {
        sumGyroZ += z;
      }
    }

    if (IMU.magneticFieldAvailable()) {
      float x, y, z;
      IMU.readMagneticField(x, y, z);
      sumMagX += x;
      sumMagY += y;
      sumMagZ += z;
    }

    if (IMU.accelerationAvailable()) {
      float x, y, z;
      IMU.readAcceleration(x, y, z);
      sumAccX += x;
      sumAccY += y;
      sumAccZ += z;
    }
  }

  gyro_offX = sumGyroX / numReadings;
  gyro_offY = sumGyroY / numReadings;
  gyro_offZ = sumGyroZ / numReadings;

  mag_offX = sumMagX / numReadings;
  mag_offY = sumMagY / numReadings;
  mag_offZ = sumMagZ / numReadings;

  acc_offX = sumAccX / numReadings;
  acc_offY = sumAccY / numReadings;
  acc_offZ = sumAccZ / numReadings;
}

void setup() {

  Serial.begin(9600);
  while (!Serial);
  Serial.println("Started");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1); 
  }
  Serial.println("Accelerometer sample rate = " + String(IMU.accelerationSampleRate()) + " Hz. In G (earth gravity).");
  Serial.println("Gyroscope sample rate = " + String(IMU.gyroscopeSampleRate()) + " Hz. In d/s (degrees/second).");
  Serial.println("Magnetometer sample rate = " + String(IMU.magneticFieldSampleRate()) + " Hz. In uT (micro Tesla).");

  if (!BARO.begin()) {
    Serial.println("Failed to initialize pressure sensor!");
    while (1);
  }
  
  Serial.println("Calculating offsets...");
  calculateAllOffsets();

}

float x, y, z;
float rx, ry, rz;
float mx, my, mz;
Vector3D acc, mag;
float dt = 0;
float roll = 0, pitch = 0, yaw = 0; // Declare roll, pitch, and yaw in the global scope

Vector3D crossProduct(const Vector3D& v1, const Vector3D& v2) {
    Vector3D result;
    result.x = v1.y * v2.z - v1.z * v2.y;
    result.y = v1.z * v2.x - v1.x * v2.z;
    result.z = v1.x * v2.y - v1.y * v2.x;
    return result;
}

float norm(float x, float y, float z) {
    return sqrt(x * x + y * y + z * z);
}

void loop() {
  unsigned long startTime = millis(); // Start time of the loop

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    float magn = norm(x,y,z);
    acc = {x/magn, y/magn, z/magn};
  }

if (IMU.gyroscopeAvailable()) {
  IMU.readGyroscope(rx, ry, rz);
  if (abs(rx - gyro_offX) > 0.1) {
    roll += (rx - gyro_offX) * dt;
  }
  if (abs(ry - gyro_offY) > 0.1) {
    pitch += (ry - gyro_offY) * dt;
  }
  if (abs(rz - gyro_offZ) > 0.1) {
    yaw += (rz - gyro_offZ) * dt;
  }
  //Serial.println("Orientation: Roll = " + String(roll, 2) + "°, Pitch = " + String(pitch, 2) + "°, Yaw = " + String(yaw, 2) + "°");
}

  if (IMU.magneticFieldAvailable()) {
    IMU.readMagneticField(mx, my, mz);
    float magn = norm(mx,my,mz);
    mag = {mx/magn, my/magn, mz/magn};
  }

  float pressure = BARO.readPressure();
  float altitude = 44330 * ( 1 - pow(pressure/101.325, 1/5.255) );

  // North East and -Acceleration form the coordinate frame of the stationary IMU, uncalibrated
  Vector3D E = crossProduct(-acc, mag);
  Vector3D N = crossProduct(E, -acc);

  float roll = atan2(E.y, E.z);
  float pitch = atan2(-E.x, sqrt(E.y * E.y + E.z * E.z));
  float yaw = atan2(N.y, N.x);
  roll = roll * 180.0 / PI;
  pitch = pitch * 180.0 / PI;
  yaw = yaw * 180.0 / PI;

  // Print the results
  Serial.println(String("Roll Pitch Yaw: ") + pitch + "," + roll + "," + yaw);

  unsigned long endTime = millis(); // End time of the loop
  dt = endTime - startTime;
}