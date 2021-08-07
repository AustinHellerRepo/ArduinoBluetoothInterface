
class HostInterface {
  public:
    void send_message_to_project(char* message, char* project_guid);
    void send_message_to_server(char* message);
};
