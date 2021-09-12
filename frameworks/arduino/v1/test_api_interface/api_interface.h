#include <ArduinoJson.h>

enum MethodTypeEnum {
  Get,
  Post
}


class ApiInterface {
  private:
    JsonObject get_json_result_from_url(MethodTypeEnum methodType, char* url, JsonObject arguments_json_object);
    char* get_formatted_url(char* url_part);
  public:
    ApiInterface(char* api_base_url);
    JsonObject test_get();
    JsonObject test_post();
    JsonObject test_json(JsonObject json_object);
    JsonObject send_device_announcement(char* device_guid, char* purpose_guid);
    JsonObject get_available_devices(char* purpose_guid);
    JsonObject send_dequeuer_announcement(char* dequeuer_guid);
    JsonObject send_reporter_announcement(char* reporter_guid);
    JsonObject send_transmission(char* queue_guid, char* source_device_guid, JsonObject transmission_json, char* destination_device_guid);
    JsonObject dequeue_next_transmission(char* dequeuer_guid, char* queue_guid);
    JsonObject update_transmission_as_completed(char* transmission_dequeue_guid);
    JsonObject update_transmission_as_failed(char* transmission_dequeue_guid, JsonObject error_message_json);
    JsonObject dequeue_next_failed_transmission(char* reporter_guid, char* queue_guid);
    JsonObject update_failed_transmission_as_completed(char* transmission_dequeue_error_transmission_dequeue_guid, bool is_retry_requested);
    JsonObject update_failed_transmission_as_failed(char* transmission_dequeue_error_transmission_dequeue_guid, JsonObject error_message_json);
    JsonObject get_uuid();
}
