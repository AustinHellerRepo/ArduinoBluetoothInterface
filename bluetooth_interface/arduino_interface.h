#include "host_interface.h"
#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include "void_callback.h"

struct HostConnectionResult {
  bool is_successful;
  HostInterface host;
};

struct process_command_output {
  int command_id;
  bool is_successful;
  int value;
};

class ArduinoInterface {
  private:
    void(*send_message_to_project)(char*);
    struct process_command_output process_command(char* command);
    VoidCallback on_interrupt_callback;
    char* last_interrupt_message;
  public:
    ArduinoInterface();
    void send_message(char* message);
    char* get_last_interrupt_message();
    struct process_command_output receive_message(char* message);
    //void set_project_message_callback(void(*send_message_to_project)(char*));
    //Event<char*> internal_message_generated;
    void on_interrupt(VoidCallback callback);
};
