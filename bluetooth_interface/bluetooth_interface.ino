
//#include "UUIDGenerator.h"
#include "helper.h"
#include "arduino_interface.h"

struct packet {
  char* message;
  char* destination_project_guid;
  char* source_project_guid;
};

struct process_command_output {
  int command_id;
  bool is_successful;
  int value;
};

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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

bool shown = false;
void loop() {
  // put your main code here, to run repeatedly:
  if (!shown) {
    Serial.println("started loop");
    shown = true;
  
    char* project_guid_0 = "first";
    char* project_guid_1 = "second";
  
    ArduinoInterface arduino;
    Serial.println("Starting 0");
    arduino.attach_fresh_project(1, project_guid_0, 2);
    arduino.display_attached_projects();
    Serial.println("Starting 1");
    arduino.attach_fresh_project(3, project_guid_1, 4);
    arduino.display_attached_projects();
    Serial.println("Starting 2");
    arduino.detach_expired_project(project_guid_1);
    arduino.display_attached_projects();
    Serial.println("Starting 3");
    arduino.detach_expired_project(project_guid_0);
    arduino.display_attached_projects();
    Serial.println("Starting 4");
  }
  
  if(Serial.available() > 0)
  {
    Serial.println("inside");
    String constructed_bluetooth_string = Serial.readString();
    int constructed_bluetooth_string_length = constructed_bluetooth_string.length();
    Serial.print("constructed_bluetooth_string_length: ");
    Serial.println(constructed_bluetooth_string_length);
    char constructed_bluetooth_chars[constructed_bluetooth_string_length];
    memcpy(constructed_bluetooth_chars, constructed_bluetooth_string.c_str(), constructed_bluetooth_string_length - 1);
    constructed_bluetooth_chars[constructed_bluetooth_string_length - 1] = '\0';
    Serial.print("input: ");
    for (int i = 0; i < constructed_bluetooth_string_length; i++) {
      Serial.println(int(constructed_bluetooth_chars[i]));
    }
    Serial.println();
    Serial.println(constructed_bluetooth_chars);
    
    struct process_command_output output;
    output = process_command(constructed_bluetooth_chars);
    Serial.print("{ command_id: ");
    Serial.print(output.command_id);
    Serial.print(", is_successful: ");
    Serial.print(output.is_successful);
    Serial.print(", value: ");
    Serial.print(output.value);
    Serial.println(" }");
    Serial.flush();
  }
}
