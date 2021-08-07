#include <stdlib.h>

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
    *t = '\0';

    return count;
};

char hex_characters[] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
char get_random_hex_value() {

  int random_index = random() % 16;
  return hex_characters[random_index];
};

char* generate_guid() {
  
  char* guid = (char*)malloc(sizeof(char) * 37);

  int guid_index = 0;
  for (int i = 0; i < 32; i++) {

    char guid_character = get_random_hex_value();
    guid[guid_index] = guid_character;

    guid_index++;

    if (i == 8 || i == 13 || i == 18 || i == 23) {
      guid[guid_index] = '-';
      guid_index++;
    }
  }

  guid[36] = 0;

  return guid;
};
