// This defines the template for the C language target

#include "stdlib.h"

#define MEMORY_SIZE %memory_size
#define STACK_SIZE %stack_size
#define REGISTER_COUNT %register_count
#define byte unsigned char

int main()
{
    byte* memory = malloc(sizeof(byte) * MEMORY_SIZE);
    if(memory == NULL)
    {
        return -1;
    }
    byte stack[STACK_SIZE];
    byte registers[REGISTER_COUNT];
    %code
    free(memory);
}