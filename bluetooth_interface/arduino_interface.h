
#include "host_interface.h"
#include <Arduino_FreeRTOS.h>
#include <semphr.h>

struct HostConnectionResult {
  bool is_successful;
  HostInterface host;
};

class ArduinoInterface {
  private:
    char** project_guids;
    SemaphoreHandle_t project_guids_semaphore;
    int project_guids_total;
    HostInterface host;
    void lock_project_guids();
    void unlock_project_guids();
  public:
    ArduinoInterface();
    void send_message_to_project(char* message, char* project_guid);
    void receive_message_from_project(char* message, char* project_guid);
    int* get_attachable_project_type_ids();
    void attach_fresh_project(int project_type_id, char* project_guid, int response_version);
    void detach_expired_project(char* project_guid);
    struct HostConnectionResult try_connect_to_network();
    void display_attached_projects();
};
