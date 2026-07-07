int main(void)
{
    int arr[10];

    int *p1 = arr;
    int *p2 = arr + 5;

    if (p1 < p2)
    {
        return 1;
    }

    return 0;
}