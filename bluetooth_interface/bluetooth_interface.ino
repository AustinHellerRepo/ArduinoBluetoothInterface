
struct process_command_output {
  int command_id;
  bool is_successful;
  int value;
};

char current_bluetooth_character = 0;
char* constructed_bluetooth_string = NULL;

int split(const char *str, char c, char ***arr)
{
    int count = 1;
    int token_len = 1;
    int i = 0;
    char *p;
    char *t;

    p = str;
    while (*p != '\0')
    {
        if (*p == c)
            count++;
        p++;
    }

    *arr = (char**) malloc(sizeof(char*) * count);
    if (*arr == NULL)
        exit(1);

    p = str;
    while (*p != '\0')
    {
        if (*p == c)
        {
            (*arr)[i] = (char*) malloc( sizeof(char) * token_len );
            if ((*arr)[i] == NULL)
                exit(1);

            token_len = 0;
            i++;
        }
        p++;
        token_len++;
    }
    (*arr)[i] = (char*) malloc( sizeof(char) * token_len );
    if ((*arr)[i] == NULL)
        exit(1);

    i = 0;
    p = str;
    t = ((*arr)[i]);
    while (*p != '\0')
    {
        if (*p != c && *p != '\0')
        {
            *t = *p;
            t++;
        }
        else
        {
            *t = '\0';
            i++;
            t = ((*arr)[i]);
        }
        p++;
    }

    return count;
}

struct process_command_output process_command(char* command) {

  Serial.print("Processing command: ");
  Serial.println(command);
  Serial.flush();

  int command_id;
  bool is_successful;
  int value;

  char** command_parts = NULL;
  int command_parts_length = split(command, ' ', &command_parts);

  command_id = atoi(command_parts[0]);
  if (strcmp(command_parts[1], "PINMODE") == 0) {
    Serial.println("Found pinMode");
    int pin_number = atoi(command_parts[2]);
    if (strcmp(command_parts[3], "OUTPUT") == 0) {
      pinMode(pin_number, OUTPUT);
      is_successful = true;
      value = 0;
    }
    else if (strcmp(command_parts[3], "INPUT") == 0) {
      pinMode(pin_number, INPUT);
      is_successful = true;
      value = 0;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else if (strcmp(command_parts[1], "DIGITALWRITE") == 0) {
    Serial.println("Found digitalWrite");
    int pin_number = atoi(command_parts[2]);
    if (strcmp(command_parts[3], "LOW") == 0) {
      digitalWrite(pin_number, LOW);
      is_successful = true;
      value = 0;
    }
    else if (strcmp(command_parts[3], "HIGH") == 0) {
      digitalWrite(pin_number, HIGH);
      is_successful = true;
      value = 0;
    }
    else {
      is_successful = false;
      value = 0;
    }
  }
  else if (strcmp(command_parts[1], "DELAY") == 0) {
    Serial.println("Found delay");
    int milliseconds = atoi(command_parts[2]);
    Serial.print("milliseconds: ");
    Serial.println(milliseconds);
    delay(milliseconds);
    is_successful = true;
    value = 0;
  }
  else if (strcmp(command_parts[1], "ANALOGREAD") == 0) {
    Serial.println("Found analogRead");
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
  else if (strcmp(command_parts[1], "ANALOGWRITE") == 0) {
    Serial.println("Found analogWrite");
    int pin_number = atoi(command_parts[2]);
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
  else if (strcmp(command_parts[1], "DIGITALREAD") == 0) {
    Serial.println("Found digitalRead");
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
    Serial.println("Not found");
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

bool shown = false;
void loop() {
  // put your main code here, to run repeatedly:
  if (!shown) {
    Serial.println("started loop");
    shown = true;
  }
  if(Serial.available() > 0)
  {
    Serial.println("inside");
    String constructed_bluetooth_string = Serial.readString();
    int constructed_bluetooth_string_length = constructed_bluetooth_string.length();
    char constructed_bluetooth_chars[constructed_bluetooth_string_length];
    strncpy(constructed_bluetooth_chars, constructed_bluetooth_string.c_str(), constructed_bluetooth_string_length - 1);
    constructed_bluetooth_chars[constructed_bluetooth_string_length - 1] = '\0';
    Serial.print("input: ");
    Serial.println(constructed_bluetooth_chars);
    
    struct process_command_output output;
    output = process_command(constructed_bluetooth_chars);
    Serial.print("{ command_id: ");
    Serial.print(output.command_id);
    Serial.print(", is_successful: ");
    Serial.print(output.is_successful);
    Serial.print(", value: ");
    Serial.print(output.value);
    Serial.println(" }");
    Serial.flush();
    constructed_bluetooth_string = "";
  }
}
