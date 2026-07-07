typedef void (*Func1)(void);
typedef int (*Func2)(void);

int foo(void)
{
    return 0;
}

int main(void)
{
    Func2 fp = (Func2)foo;
    return 0;
}