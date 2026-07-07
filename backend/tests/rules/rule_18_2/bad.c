int main(void)
{
    int arr1[5];
    int arr2[5];

    int *p1 = arr1;
    int *p2 = arr2;

    int diff = p1 - p2;

    return diff;
}