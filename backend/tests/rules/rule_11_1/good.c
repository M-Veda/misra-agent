typedef int (*Func2)(void);

int foo(void)
{
    return 0;
}

int main(void)
{
    Func2 fp = foo;
    return 0;
}