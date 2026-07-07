void helper(void)
{
}

void foo(void)
{
    helper();
}

void bar(void)
{
    helper();
}

int main(void)
{
    foo();
    bar();
    return 0;
}