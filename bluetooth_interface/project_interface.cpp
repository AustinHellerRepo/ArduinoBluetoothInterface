
#include "project_interface.h"
#include "helper.h"
#include <Arduino.h>

/*class ProjectInterface {
  private:
    ArduinoInterface arduino;
    ProjectInterface* attached_projects;
  public:
    void send_message(char* message);
    ProjectInterface(ArduinoInterface arduino);
    ProjectInterface(char* remote_project_guid);
}*/


void send_message_from_arduino_to_project(char* message, ProjectInterface* project) {

  project->receive_message_from_arduino(message);
}

ProjectInterface::ProjectInterface(ArduinoInterface* arduino, char* project_guid, int project_type_id, int response_version) {

  this->arduino = arduino;
  this->project_guid = project_guid;
  this->project_type_id = project_type_id;
  this->response_version = response_version;
  this->remote_projects = new ProjectInterface*[0];
  this->remote_projects_total = 0;
  this->host = NULL;
  this->remote_projects_semaphore = xSemaphoreCreateMutex();

  if (this->remote_projects_semaphore == NULL) {
    Serial.println("Failed to initialize remote_projects_semaphore.");
  }
  
  //this->arduino->set_project_message_callback(this->receive_message_from_arduino);
  this->arduino->on_interrupt([&](){
    this->receive_message_from_arduino(this->arduino->get_last_interrupt_message());
  });
}

struct process_command_output ProjectInterface::send_message(char* message) {

  if (this->arduino != NULL) {
    // this project is the current project on the local arduino
    struct process_command_output output = this->arduino->receive_message(message);
    return output;
  }
}

void ProjectInterface::display_remote_projects() {

  for (int i = 0; i < this->remote_projects_total; i++) {
    Serial.print("project: ");
    Serial.println(this->remote_projects[i]->get_project_guid());
  }
}

char* ProjectInterface::get_project_guid() {
  return this->project_guid;
}

void ProjectInterface::attach_fresh_project(ProjectInterface* project) {

  this->lock_remote_projects();

  ProjectInterface** remote_projects = new ProjectInterface*[this->remote_projects_total + 1];
  for (int i = 0; i < this->remote_projects_total; i++) {
    remote_projects[i] = this->remote_projects[i];
  }

  remote_projects[this->remote_projects_total] = project;
  this->remote_projects_total++;

  delete this->remote_projects;
  this->remote_projects = remote_projects;

  this->unlock_remote_projects();
}

void ProjectInterface::detach_expired_project(ProjectInterface* project) {

  this->lock_remote_projects();

  int remote_project_index = -1;
  for (int i = 0; i < this->remote_projects_total; i++) {
    if (strcmp(this->remote_projects[i]->get_project_guid(), project->get_project_guid()) == 0) {
      remote_project_index = i;
      break;
    }
  }

  if (remote_project_index == -1) {
    Serial.print("Failed to find expired project \"");
    Serial.print(project->get_project_guid());
    Serial.println("\".");
  }
  else {
    ProjectInterface** remote_projects = new ProjectInterface*[this->remote_projects_total - 1];
    int remote_projects_index = 0;
    for (int i = 0; i < this->remote_projects_total; i++) {
      if (i != remote_project_index) {
        remote_projects[remote_projects_index] = this->remote_projects[i];
        remote_projects_index++;
      }
    }

    this->remote_projects_total--;

    delete this->remote_projects;
    this->remote_projects = remote_projects;
  }

  this->unlock_remote_projects();
}

void ProjectInterface::lock_remote_projects() {

  bool is_locked = false;
  while (!is_locked) {
    if (xSemaphoreTake(this->remote_projects_semaphore, portMAX_DELAY) == pdPASS) {
      is_locked = true;
    }
  }
}

void ProjectInterface::unlock_remote_projects() {

  xSemaphoreGiveFromISR(this->remote_projects_semaphore, NULL);
}

int* ProjectInterface::get_related_project_type_ids() {

  Serial.println("Error: get_related_project_type_ids must be implemented by child class.");
}

struct HostConnectionResult ProjectInterface::try_connect_to_server() {

  if (this->host == NULL) {
    Serial.println("Failed to announce existence while not connected to host.");
  }
  else {
    char message[] = "";
    strcat(message, "{ version: 1, project_guid: \"");
    strcat(message, this->project_guid);
    strcat(message, "\" }");
    this->host->send_message_to_server(message);
  }
}
