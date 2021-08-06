#include <stdlib.h>
#include <string.h>
#include "arduino_interface.h"
#include <Arduino.h>

ArduinoInterface::ArduinoInterface() {
  this->project_guids_total = 0;
  this->project_guids = (char**)malloc(sizeof(char*) * this->project_guids_total);

  //Serial.println("Initializing semaphore.");
  
  this->project_guids_semaphore = xSemaphoreCreateMutex();

  if (this->project_guids_semaphore == NULL) {
    Serial.println("Failed to initialize project_guids_semaphore.");
  }
}

void ArduinoInterface::lock_project_guids() {

  bool is_locked = false;
  while (!is_locked) {
    if (xSemaphoreTake(this->project_guids_semaphore, portMAX_DELAY) == pdPASS) {
      is_locked = true;
    }
  }
}

void ArduinoInterface::unlock_project_guids() {

  xSemaphoreGiveFromISR(this->project_guids_semaphore, NULL);
}

void ArduinoInterface::send_message_to_project(char* message, char* project_guid) {

  this->host.send_message(message, project_guid);
}

void ArduinoInterface::receive_message_from_project(char* message, char* project_guid) {

  Serial.println("Error: receive_message_from_project must be implemented by child class.");
}

int* ArduinoInterface::get_attachable_project_type_ids() {

  Serial.println("Error: get_attachable_project_type_ids must be implemented by child class.");
}

void ArduinoInterface::attach_fresh_project(int project_type_id, char* project_guid, int response_version) {

  this->lock_project_guids();

  char** project_guids = new char*[this->project_guids_total + 1];
  for (int i = 0; i < this->project_guids_total; i++) {
    project_guids[i] = this->project_guids[i];
  }
  
  project_guids[this->project_guids_total] = project_guid;
  this->project_guids_total++;

  delete this->project_guids;
  this->project_guids = project_guids;
  
  this->unlock_project_guids();
}

void ArduinoInterface::detach_expired_project(char* project_guid) {

  this->lock_project_guids();

  int project_guid_index = -1;
  for (int i = 0; i < this->project_guids_total; i++) {
    if (strcmp(this->project_guids[i], project_guid) == 0) {
      project_guid_index = i;
      break;
    }
  }

  if (project_guid_index == -1) {
    Serial.print("Failed to find expired project \"");
    Serial.print(project_guid);
    Serial.println("\".");
  }
  else {
    char** project_guids = new char*[this->project_guids_total - 1];
    int project_guids_index = 0;
    for (int i = 0; i < this->project_guids_total; i++) {
      if (i != project_guid_index) {
        project_guids[project_guids_index] = this->project_guids[i];
      }
    }

    this->project_guids_total--;
    
    delete this->project_guids;
    this->project_guids = project_guids;
  }

  this->unlock_project_guids();
}

struct HostConnectionResult try_connect_to_network() {

  Serial.println("Error: try_connect_to_network must be implemented by child class.");
}

void ArduinoInterface::display_attached_projects() {

  for (int i = 0; i < this->project_guids_total; i++) {
    Serial.print("project: ");
    Serial.println(this->project_guids[i]);
  }
}
