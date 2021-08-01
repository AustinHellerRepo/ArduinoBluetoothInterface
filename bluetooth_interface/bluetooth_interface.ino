
struct process_command_output {
  int command_id;
  bool is_successful;
  int value;
};

char current_bluetooth_character = 0;
char* constructed_bluetooth_string = "";

void split_string(char* to_split, char delimiter, char** strings) {
  int delimiters_total = 0;
  //int string_length = to_split.length();
  int string_length = strlen(to_split);
  for(int i = 0; i < string_length; i++) {
    //char character_at_index = to_split.charAt(i);
    char character_at_index = to_split[i];
    if(character_at_index == delimiter) {
      delimiters_total += 1;
    }
  }
  int delimiter_indexes[delimiters_total];
  int delimiter_indexes_index = 0;
  for(int i = 0; i < string_length; i++) {
    //char character_at_index = to_split.charAt(i);
    char character_at_index = to_split[i];
    if(character_at_index == delimiter) {
      delimiter_indexes[delimiter_indexes_index] = i;
      delimiter_indexes_index += 1;
    }
  }
  
  char* split_result[delimiters_total + 1];
  int previous_index = 0;
  int next_index = string_length;
  
  for (int i = 0; i < delimiters_total; i++) {
    next_index = delimiter_indexes[i];
    //char* split_substring;
    //split_substring = to_split.substring(previous_index, next_index);
    char split_substring[next_index - previous_index];
    memcpy(split_substring, &to_split[previous_index], next_index - previous_index - 1);
    split_substring[next_index - previous_index] = '\0';
    //Serial.print("Substring: ");
    //Serial.println(split_substring);
    //split_result[i] = split_substring;
    strcpy(split_result[i], split_substring);
    previous_index = next_index + 1;
  }
  //split_substring = to_split.substring(previous_index);
  char split_substring[next_index - previous_index];
  memcpy(split_substring, &to_split[previous_index], next_index);
  //split_result[delimiters_total] = split_substring;
  strcpy(split_result[0], split_substring);

  return split_result;
}

struct process_command_output process_command(char* command) {

  Serial.print("Processing command: ");
  Serial.println(command);
  Serial.flush();

  int command_id;
  bool is_successful;
  int value;

  //String* command_parts = split_string(command, ' ');
  char** command_parts;
  split_string(command, ' ', command_parts);

  //command_id = command_parts[0].toInt();
  command_id = atoi(command_parts[0]);
  if (command_parts[1] == "PINMODE") {
    //int pin_number = command_parts[2].toInt();
    int pin_number = atoi(command_parts[2]);
    if (command_parts[3] == "OUTPUT") {
      pinMode(pin_number, OUTPUT);
      is_successful = true;
      value = 0;
    }
    else if (command_parts[3] == "INPUT") {
      pinMode(pin_number, INPUT);
      is_successful = true;
      value = 0;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else if (command_parts[1] == "DIGITALWRITE") {
    //int pin_number = command_parts[2].toInt();
    int pin_number = atoi(command_parts[2]);
    if (command_parts[3] == "LOW") {
      digitalWrite(pin_number, LOW);
      is_successful = true;
      value = 0;
    }
    else if (command_parts[3] == "HIGH") {
      digitalWrite(pin_number, HIGH);
      is_successful = true;
      value = 0;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else if (command_parts[1] == "DELAY") {
    //int milliseconds = command_parts[2].toInt();
    int milliseconds = atoi(command_parts[2]);
    delay(milliseconds);
    is_successful = true;
    value = 0;
  }
  else if (command_parts[1] == "ANALOGREAD") {
    //int pin_number = command_parts[2].toInt();
    int pin_number = atoi(command_parts[2]);
    is_successful = true;
    value = analogRead(pin_number);
  }
  /*else if (command_parts[1] == "ANALOGREADRESOLUTION") {
    int bits_total = command_parts[2].toInt();
    analogReadResolution(bits_total);
    is_successful = true;
    value = 0;
  }*/
  else if (command_parts[1] == "ANALOGWRITE") {
    //int pin_number = command_parts[2].toInt();
    int pin_number = atoi(command_parts[2]);
    //int pin_value = command_parts[3].toInt();
    int pin_value = atoi(command_parts[3]);
    analogWrite(pin_number, pin_value);
    is_successful = true;
    value = 0;
  }
  /*else if (command_parts[1] == "ANALOGWRITERESOLUTION") {
    int bits_total = command_parts[2].toInt();
    analogWriteResolution(bits_total)
    is_successful = true;
    value = 0;
  }*/
  else if (command_parts[1] == "DIGITALREAD") {
    //int pin_number = command_parts[2].toInt();
    int pin_number = atoi(command_parts[2]);
    int digital_read_output = digitalRead(pin_number);
    if (digital_read_output == LOW) {
      is_successful = true;
      value = 0;
    }
    else if (digital_read_output == HIGH) {
      is_successful = true;
      value = 1;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else {
    is_successful = false;
    value = 0;
  }

  struct process_command_output output;
  output.command_id = command_id;
  output.is_successful = is_successful;
  output.value = value;
  return output;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

int temp = 0;
void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0)
  {
    current_bluetooth_character = Serial.read();
    if (current_bluetooth_character != '\n') {
      Serial.print("Found character: ");
      Serial.println(current_bluetooth_character);
      strncat(constructed_bluetooth_string, &current_bluetooth_character, 1);
    }
    else {
      temp++;
      struct process_command_output output;
      output = process_command(constructed_bluetooth_string);
      Serial.print("{ command_id: ");
      Serial.print(output.command_id);
      Serial.print(temp);
      Serial.print(", is_successful: ");
      Serial.print(output.is_successful);
      Serial.print(", value: ");
      Serial.print(output.value);
      Serial.println(" }");
      Serial.flush();
      constructed_bluetooth_string = "";        
    }
  }
}
