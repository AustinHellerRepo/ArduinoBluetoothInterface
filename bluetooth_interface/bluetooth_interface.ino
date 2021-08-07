
//#include "UUIDGenerator.h"
#include "helper.h"
#include "project_interface.h"

struct packet {
  char* message;
  char* destination_project_guid;
  char* source_project_guid;
};



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // initialize random seed
  int current_seed_offset = 0;
  for (int i = 0; i < 10; i++) {
    randomSeed(analogRead(0) + current_seed_offset);
    current_seed_offset += random();
  }
}

void example(char* msg) {
  Serial.print("Found message: ");
  Serial.println(msg);
}

ProjectInterface* project = new ProjectInterface(new ArduinoInterface(), generate_guid(), 1, 1);

bool shown = false;
void loop() {
  // put your main code here, to run repeatedly:
  if (!shown) {
    Serial.println("started loop");
    shown = true;
  
    const char* project_guid_0 = "first";
    const char* project_guid_1 = "second";

    ArduinoInterface* arduino = new ArduinoInterface();

    ProjectInterface* project_0 = new ProjectInterface(arduino, generate_guid(), 1, 2);
    ProjectInterface* project_1 = new ProjectInterface(NULL, generate_guid(), 3, 4);
    ProjectInterface* project_2 = new ProjectInterface(NULL, generate_guid(), 5, 6);
 
    Serial.println("Starting 0");
    project_0->attach_fresh_project(project_1);
    project_0->display_remote_projects();
    Serial.println("Starting 1");
    project_0->attach_fresh_project(project_2);
    project_0->display_remote_projects();
    Serial.println("Starting 2");
    project_0->detach_expired_project(project_2);
    project_0->display_remote_projects();
    Serial.println("Starting 3");
    project_0->detach_expired_project(project_1);
    project_0->display_remote_projects();
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
    //output = process_command(constructed_bluetooth_chars);
    output = project->send_message(constructed_bluetooth_chars);
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
