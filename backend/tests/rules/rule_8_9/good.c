int value;

void foo(void)
{
    value = 10;
}

void bar(void)
{
    value = 20;
}

int main(void)
{
    foo();
    bar();
    return 0;
}