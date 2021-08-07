#include <stdlib.h>
#include <string.h>
#include "arduino_interface.h"
#include <Arduino.h>
#include "helper.h"

ArduinoInterface::ArduinoInterface() {
  this->last_interrupt_message = NULL;
}

/*void ArduinoInterface::set_project_message_callback(void(*send_message_to_project)(char*)) {
  this->send_message_to_project = (*send_message_to_project);
}*/

void ArduinoInterface::on_interrupt(VoidCallback callback) {
  this->on_interrupt_callback = callback;
}

void ArduinoInterface::send_message(char* message) {

  this->send_message_to_project(message);
}

struct process_command_output ArduinoInterface::receive_message(char* message) {

  struct process_command_output output = this->process_command(message);
  return output;
}

struct process_command_output process_command(char* command) {

  Serial.print("Processing command: ");
  Serial.println(command);
  Serial.flush();

  int command_id;
  bool is_successful;
  int value;

  char** command_parts = NULL;
  int command_parts_length = split(command, ' ', &command_parts);

  for (int i = 0; i < command_parts_length; i++) {
    Serial.print("Part ");
    Serial.print(i);
    Serial.print(": ");
    Serial.println(command_parts[i]);
  }

  command_id = atoi(command_parts[0]);
  if (strcmp(command_parts[1], "PINMODE") == 0) {
    Serial.println("Found pinMode");
    int pin_number = atoi(command_parts[2]);
    if (strcmp(command_parts[3], "OUTPUT") == 0) {
      pinMode(pin_number, OUTPUT);
      is_successful = true;
      value = 0;
    }
    else if (strcmp(command_parts[3], "INPUT") == 0) {
      pinMode(pin_number, INPUT);
      is_successful = true;
      value = 0;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else if (strcmp(command_parts[1], "DIGITALWRITE") == 0) {
    Serial.println("Found digitalWrite");
    int pin_number = atoi(command_parts[2]);
    if (strcmp(command_parts[3], "LOW") == 0) {
      digitalWrite(pin_number, LOW);
      is_successful = true;
      value = 0;
    }
    else if (strcmp(command_parts[3], "HIGH") == 0) {
      digitalWrite(pin_number, HIGH);
      is_successful = true;
      value = 0;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else if (strcmp(command_parts[1], "DELAY") == 0) {
    Serial.println("Found delay");
    int milliseconds = atoi(command_parts[2]);
    Serial.print("milliseconds: ");
    Serial.println(milliseconds);
    delay(milliseconds);
    is_successful = true;
    value = 0;
  }
  else if (strcmp(command_parts[1], "ANALOGREAD") == 0) {
    Serial.println("Found analogRead");
    int pin_number = atoi(command_parts[2]);
    is_successful = true;
    value = analogRead(pin_number);
  }
  /*else if (command_parts[1] == "ANALOGREADRESOLUTION") {
    int bits_total = command_parts[2].toInt();
    analogReadResolution(bits_total);
    is_successful = true;
    value = 0;
  }*/
  else if (strcmp(command_parts[1], "ANALOGWRITE") == 0) {
    Serial.println("Found analogWrite");
    int pin_number = atoi(command_parts[2]);
    int pin_value = atoi(command_parts[3]);
    analogWrite(pin_number, pin_value);
    is_successful = true;
    value = 0;
  }
  /*else if (command_parts[1] == "ANALOGWRITERESOLUTION") {
    int bits_total = command_parts[2].toInt();
    analogWriteResolution(bits_total)
    is_successful = true;
    value = 0;
  }*/
  else if (strcmp(command_parts[1], "DIGITALREAD") == 0) {
    Serial.println("Found digitalRead");
    int pin_number = atoi(command_parts[2]);
    int digital_read_output = digitalRead(pin_number);
    if (digital_read_output == LOW) {
      is_successful = true;
      value = 0;
    }
    else if (digital_read_output == HIGH) {
      is_successful = true;
      value = 1;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else {
    Serial.println("Not found");
    is_successful = false;
    value = 0;
  }

  struct process_command_output output;
  output.command_id = command_id;
  output.is_successful = is_successful;
  output.value = value;
  
  return output;
}
