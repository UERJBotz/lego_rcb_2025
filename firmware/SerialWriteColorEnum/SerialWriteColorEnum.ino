#include "Ev3ColorSensor.h"

Ev3ColorSensor sensor(8, 7);

void setup(){
    Serial.begin(115200);
    sensor.begin();
}

void loop(){
    Ev3ColorResult color = sensor.read();
    Serial.write(color.color);
}
