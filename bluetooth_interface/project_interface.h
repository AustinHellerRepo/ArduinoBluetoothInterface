
#include "arduino_interface.h"

class ProjectInterface {
  private:
    ArduinoInterface* arduino;
    char* project_guid;
    int project_type_id;
    int response_version;
    ProjectInterface** remote_projects;
    SemaphoreHandle_t remote_projects_semaphore;
    int remote_projects_total;
    HostInterface* host;
    void lock_remote_projects();
    void unlock_remote_projects();
  public:
    struct process_command_output send_message(char* message);
    struct HostConnectionResult try_connect_to_server();
    ProjectInterface(ArduinoInterface* arduino, char* project_guid, int project_type_id, int response_version);
    void display_remote_projects();
    char* get_project_guid();
    void attach_fresh_project(ProjectInterface* project);
    void detach_expired_project(ProjectInterface* project);
    int* get_related_project_type_ids();
    void receive_message_from_arduino(char* message);
};
