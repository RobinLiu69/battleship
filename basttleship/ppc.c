#include <stdio.h>

int main(){

    char a[5] = "hello";
    a[0] = 'p';

    printf("%s\n", a);

    char *b = "hello";

    printf("%s\n", b);


    return 0;
}