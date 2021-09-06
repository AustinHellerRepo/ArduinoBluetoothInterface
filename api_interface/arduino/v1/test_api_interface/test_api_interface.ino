
#include <Wifi.h>
#include <HTTPClient.h>
#include <api_interface.h>

const char* wifi_ssid = "EXAMPLE_SSID";
const char* wifi_password = "EXAMPLE_PASSWORD";

const char* device_messaging_server_base_url = "http://0.0.0.0:80"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  Serial.println("Connecting");
  Wifi.begin(wifi_ssid, wifi_password);
  while(Wifi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to Wifi network with IP address \"");
  Serial.print(Wifi.localIP());
  Serial.println("\".");
}

void loop() {
  // put your main code here, to run repeatedly:

}
