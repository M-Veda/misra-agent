#include<stdio.h>
#include<stdlib.h>

int global = 0;

void func(int a)
{
    if(a = 5)
    {
        printf("Equal\n");
    }
}

int main(void)
{
    int i;
    int arr[5];

    for(i = 0; i <= 5; i++)
    {
        arr[i] = i * 10;
    }

    char *ptr = malloc(10);

    gets(ptr);

    if(ptr != NULL)
        printf(ptr);

    func(3);

    return;
}