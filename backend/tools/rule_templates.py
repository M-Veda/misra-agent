RULE_TESTS = {

    # =====================================================
    # Chapter 7
    # =====================================================

    "7.1": {
        "bad": r"""
int main(void)
{
    unsigned int x = 0123;
    return x;
}
""",
        "good": r"""
int main(void)
{
    unsigned int x = 123U;
    return x;
}
""",
        "violations": 1,
    },

    "7.2": {
        "bad": r"""
int main(void)
{
    unsigned int x = 10l;
    return x;
}
""",
        "good": r"""
int main(void)
{
    unsigned long x = 10UL;
    return 0;
}
""",
        "violations": 1,
    },

    "7.3": {
        "bad": r"""
int main(void)
{
    int x = 10;
    return x;
}
""",
        "good": r"""
int main(void)
{
    int x = 10U;
    return x;
}
""",
        "violations": 1,
    },

    "7.4": {
        "bad": r"""
int main(void)
{
    float x = 10.0;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    float x = 10.0F;
    return 0;
}
""",
        "violations": 1,
    },

    "7.5": {
        "bad": r"""
int main(void)
{
    double d = 1.0f;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    double d = 1.0;
    return 0;
}
""",
        "violations": 1,
    },

    "7.6": {
        "bad": r"""
int main(void)
{
    long x = 1l;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    long x = 1L;
    return 0;
}
""",
        "violations": 1,
    },

    "7.7": {
        "bad": r"""
int main(void)
{
    unsigned int x = 100;
    return x;
}
""",
        "good": r"""
int main(void)
{
    unsigned int x = 100U;
    return x;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 8
    # =====================================================

    "8.1": {
        "bad": r"""
int func();

int main(void)
{
    return 0;
}
""",
        "good": r"""
int func(void);

int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "8.2": {
        "bad": r"""
int add(int, int);
""",
        "good": r"""
int add(int a, int b);
""",
        "violations": 1,
    },

    "8.3": {
        "bad": r"""
int add(int);
int add(char);
""",
        "good": r"""
int add(int);
int add(int);
""",
        "violations": 1,
    },

    "8.4": {
        "bad": r"""
int func(void)
{
    return 0;
}
""",
        "good": r"""
int func(void);

int func(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "8.5": {
        "bad": r"""
extern int value;
extern int value;
""",
        "good": r"""
extern int value;
""",
        "violations": 1,
    },

    "8.6": {
        "bad": r"""
static int counter;
""",
        "good": r"""
static int counter = 0;
""",
        "violations": 1,
    },

    "8.7": {
        "bad": r"""
int unused_global;
""",
        "good": r"""
static int unused_global;
""",
        "violations": 1,
    },

    "8.8": {
        "bad": r"""
extern int x;
int x;
""",
        "good": r"""
extern int x;
""",
        "violations": 1,
    },

    "8.9": {
        "bad": r"""
int value;
""",
        "good": r"""
static int value;
""",
        "violations": 1,
    },

    "8.10": {
        "bad": r"""
inline int add(int a,int b)
{
    return a+b;
}
""",
        "good": r"""
static inline int add(int a,int b)
{
    return a+b;
}
""",
        "violations": 1,
    },

    "8.11": {
        "bad": r"""
int value;
""",
        "good": r"""
extern int value;
""",
        "violations": 1,
    },

    "8.12": {
        "bad": r"""
enum
{
    RED,
    RED
};
""",
        "good": r"""
enum
{
    RED,
    BLUE
};
""",
        "violations": 1,
    },

    "8.13": {
        "bad": r"""
int *ptr;
""",
        "good": r"""
const int *ptr;
""",
        "violations": 1,
    },

    "8.14": {
        "bad": r"""
int buffer[10];
""",
        "good": r"""
static int buffer[10];
""",
        "violations": 1,
    },


    # =====================================================
    # Chapter 9
    # =====================================================

    "9.1": {
        "bad": r"""
int main(void)
{
    int x;
    return x;
}
""",
        "good": r"""
int main(void)
{
    int x = 0;
    return x;
}
""",
        "violations": 1,
    },

    "9.2": {
        "bad": r"""
int main(void)
{
    int a[3];
    return a[0];
}
""",
        "good": r"""
int main(void)
{
    int a[3] = {1,2,3};
    return a[0];
}
""",
        "violations": 1,
    },

    "9.3": {
        "bad": r"""
int main(void)
{
    int x;
    return x;
}
""",
        "good": r"""
int main(void)
{
    int x = 10;
    return x;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 10
    # =====================================================

    "10.1": {
        "bad": r"""
int main(void)
{
    int x;
    x = 3.14f;
    return x;
}
""",
        "good": r"""
int main(void)
{
    int x;
    x = 3;
    return x;
}
""",
        "violations": 1,
    },

    "10.2": {
        "bad": r"""
int main(void)
{
    char c='A';
    int x=c+1;
    return x;
}
""",
        "good": r"""
int main(void)
{
    int x=1+2;
    return x;
}
""",
        "violations": 1,
    },

    "10.3": {
        "bad": r"""
int main(void)
{
    int x;
    float y=1.5f;
    x=y;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int x;
    int y=2;
    x=y;
    return 0;
}
""",
        "violations": 1,
    },

    "10.4": {
        "bad": r"""
int main(void)
{
    int a=1;
    float b=2.0f;
    int c=a+b;
    return c;
}
""",
        "good": r"""
int main(void)
{
    int a=1;
    int b=2;
    int c=a+b;
    return c;
}
""",
        "violations": 1,
    },

    "10.5": {
        "bad": r"""
int main(void)
{
    int x=(int)3.5f;
    return x;
}
""",
        "good": r"""
int main(void)
{
    int x=3;
    return x;
}
""",
        "violations": 1,
    },

    "10.6": {
        "bad": r"""
int main(void)
{
    long l;
    int a=1,b=2;
    l=a+b;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a=1,b=2;
    int c=a+b;
    return c;
}
""",
        "violations": 1,
    },

    "10.7": {
        "bad": r"""
int main(void)
{
    int a=1;
    float b=2.0f;
    double c=3.0;
    double d=a+b+c;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a=1,b=2,c=3;
    int d=a+b+c;
    return d;
}
""",
        "violations": 1,
    },

    "10.8": {
        "bad": r"""
int main(void)
{
    int a=1,b=2;
    float c=(float)(a+b);
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a=1,b=2;
    int c=a+b;
    return c;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 11
    # =====================================================

    "11.1": {
        "bad": r"""
int main(void)
{
    int (*fp)(void);
    void *p = fp;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int (*fp)(void);
    (void)fp;
    return 0;
}
""",
        "violations": 1,
    },

    "11.2": {
        "bad": r"""
int main(void)
{
    int *p;
    float *q = (float *)p;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int *p;
    (void)p;
    return 0;
}
""",
        "violations": 1,
    },

    "11.3": {
        "bad": r"""
int main(void)
{
    int x;
    void *p = (void *)&x;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int x;
    int *p = &x;
    return 0;
}
""",
        "violations": 1,
    },

    "11.4": {
        "bad": r"""
int main(void)
{
    int *p;
    long *q = (long *)p;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int *p;
    int *q = p;
    return 0;
}
""",
        "violations": 1,
    },

    "11.5": {
        "bad": r"""
int main(void)
{
    const int *p = 0;
    int *q = (int *)p;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    const int *p = 0;
    const int *q = p;
    return 0;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 13
    # =====================================================

    "13.2": {
        "bad": r"""
int i=0;
int main(void)
{
    if(i++ + i++)
    {
    }
    return 0;
}
""",
        "good": r"""
int i=0;
int main(void)
{
    i++;
    if(i)
    {
    }
    return 0;
}
""",
        "violations": 1,
    },

    "13.3": {
        "bad": r"""
int i=0;
int main(void)
{
    i=i++;
    return 0;
}
""",
        "good": r"""
int i=0;
int main(void)
{
    i++;
    return 0;
}
""",
        "violations": 1,
    },

    "13.4": {
        "bad": r"""
int i=0;
int main(void)
{
    int x=i++;
    return x;
}
""",
        "good": r"""
int i=0;
int main(void)
{
    i++;
    return i;
}
""",
        "violations": 1,
    },

    "13.5": {
        "bad": r"""
int i=0;
int main(void)
{
    if(i && i++)
    {
    }
    return 0;
}
""",
        "good": r"""
int i=0;
int main(void)
{
    if(i)
    {
    }
    return 0;
}
""",
        "violations": 1,
    },

    "13.6": {
        "bad": r"""
int i=0;
int main(void)
{
    sizeof(i++);
    return 0;
}
""",
        "good": r"""
int i=0;
int main(void)
{
    sizeof(i);
    return 0;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 15
    # =====================================================

    "15.1": {
        "bad": r"""
int main(void)
{
    goto end;
end:
    return 0;
}
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "15.2": {
        "bad": r"""
int main(void)
{
label:
    return 0;
}
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "15.3": {
        "bad": r"""
int main(void)
{
    goto exit;
    return 0;
exit:
    return 0;
}
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "15.4": {
        "bad": r"""
int main(void)
{
    while(1)
    {
        break;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "15.5": {
        "bad": r"""
int main(void)
{
    if(1)
        return 0;
    return 1;
}
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "15.6": {
        "bad": r"""
int main(void)
{
    if(1)
        return 0;
}
""",
        "good": r"""
int main(void)
{
    if(1)
    {
        return 0;
    }
    return 0;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 16
    # =====================================================

    "16.1": {
        "bad": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            ;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        default:
            break;
    }
    return 0;
}
""",
        "violations": 1,
    },

    "16.3": {
        "bad": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            ;
        case 2:
            break;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        case 2:
            break;
        default:
            break;
    }
    return 0;
}
""",
        "violations": 1,
    },

    "16.4": {
        "bad": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        default:
            break;
    }
    return 0;
}
""",
        "violations": 1,
    },

    "16.5": {
        "bad": r"""
int main(void)
{
    switch(1)
    {
        default:
            break;
        case 1:
            break;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        default:
            break;
    }
    return 0;
}
""",
        "violations": 1,
    },

    "16.6": {
        "bad": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        case 2:
            break;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        case 2:
            break;
        default:
            break;
    }
    return 0;
}
""",
        "violations": 1,
    },

    "16.7": {
        "bad": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
    }
    return 0;
}
""",
        "good": r"""
int main(void)
{
    switch(1)
    {
        case 1:
            break;
        default:
            break;
    }
    return 0;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 17
    # =====================================================

    "17.2": {
        "bad": r"""
int f(void)
{
    return f();
}
""",
        "good": r"""
int f(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 18
    # =====================================================

    "18.1": {
        "bad": r"""
int main(void)
{
    int a[5];
    int *p = &a[6];
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a[5];
    int *p = &a[4];
    return 0;
}
""",
        "violations": 1,
    },

    "18.2": {
        "bad": r"""
int main(void)
{
    int a[5];
    int *p = a;
    p = p + 10;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a[5];
    int *p = a;
    p = p + 1;
    return 0;
}
""",
        "violations": 1,
    },

    "18.3": {
        "bad": r"""
int main(void)
{
    int a[5];
    int *p = a;
    int *q = p + 6;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a[5];
    int *p = a;
    int *q = p + 1;
    return 0;
}
""",
        "violations": 1,
    },

    "18.4": {
        "bad": r"""
int main(void)
{
    int *p;
    p++;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int x;
    int *p = &x;
    p = &x;
    return 0;
}
""",
        "violations": 1,
    },

    "18.5": {
        "bad": r"""
int main(void)
{
    int a[5];
    int *p = a;
    int *q = p + 100;
    return 0;
}
""",
        "good": r"""
int main(void)
{
    int a[5];
    int *p = a;
    int *q = p;
    return 0;
}
""",
        "violations": 1,
    },

    # =====================================================
    # Chapter 20
    # =====================================================

    "20.1": {
        "bad": r"""
#include "a.h"
#include <stdio.h>
""",
        "good": r"""
#include <stdio.h>
""",
        "violations": 1,
    },

    "20.2": {
        "bad": r"""
#define int float

int main(void)
{
    return 0;
}
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "20.3": {
        "bad": r"""
#undef EOF
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "20.4": {
        "bad": r"""
#define malloc(x) x
""",
        "good": r"""
int main(void)
{
    return 0;
}
""",
        "violations": 1,
    },

    "20.5": {
        "bad": r"""
#include "a.h"
#include "a.h"
""",
        "good": r"""
#include "a.h"
""",
        "violations": 1,
    },
}