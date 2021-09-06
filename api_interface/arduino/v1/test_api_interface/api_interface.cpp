#include "api_interface.h"


ApiInterface::ApiInterface(char* api_base_url) {
  this->api_base_url = api_base_url
}


JsonObject ApiInterface::get_json_result_from_url(MethodTypeEnum methodType, char* url, JsonObject arguments_json_object) {
  WifiClient client;
  HTTPClient http;

  http.begin(client, url);

  int httpResponseStatusCode;
  switch (methodType) {
    case MethodTypeEnum.Get: {
      httpResponseStatusCode = http.GET();
      break;
    }
    case MethodTypeEnum.Post: {
      // TODO
    }
  }

  String response;
  if (httpResponseStatusCode > 0) {
    response = http.getString();
  }
  else {
    response = null;
  }

  http.end();

  
}

char* ApiInterface::get_formatted_url(char* url_part) {
  int api_base_url_length = strlen(this->api_base_url);
  int url_part_length = strlen(url_part);
  char* formatted_url = (char*)malloc(api_base_url_length + 1 + url_part_length + 1);
  int formatted_url_index = 0;
  for (int i = 0; i < api_base_url_length; i++) {
    formatted_url[formatted_url_index] = this->api_base_url[i];
    formatted_url_index++;
  }
  formatted_url[formatted_url_index] = '/';
  formatted_url_index++;
  for (int i = 0; i < url_part_length; i++) {
    formatted_url[formatted_url_index] = url_part[i];
    formatted_url_index++;
  }
  formatted_url[formatted_url_index] = 0;
  return formatted_url;
}
