// dirty_c.c — memory leaks for AST engine testing

#include <stdio.h>
#include <stdlib.h>

int main() {
    // malloc without free
    int *ptr = malloc(sizeof(int) * 10);
    ptr[0] = 42;

    // fopen without fclose
    FILE *f = fopen("data.txt", "r");

    // dangling pointer — ptr reassigned before free
    ptr = malloc(sizeof(int) * 20);

    return 0;
}
