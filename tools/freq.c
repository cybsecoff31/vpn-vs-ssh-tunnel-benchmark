#include <stdio.h>
#include <time.h>
#include <stdint.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec*1e-9;}
#define R8(x) x x x x x x x x
#define R64(x) R8(R8(x))
int main(void){uint64_t n=20000000,a=1,b=3;for(int k=0;k<5;k++){uint64_t i=n;double t=now();
__asm__ volatile("1:" R64("add %0,%0,%1\n") "subs %2,%2,#1\n b.ne 1b\n":"+r"(a),"+r"(b),"+r"(i)::"cc");
double add=now()-t;i=n/3;t=now();
__asm__ volatile("2:" R64("mul %0,%0,%1\n") "subs %2,%2,#1\n b.ne 2b\n":"+r"(a),"+r"(b),"+r"(i)::"cc");
double mul=now()-t;printf("add-chain %.3f GHz   mul-chain (3 cycles) %.3f GHz\n",n*64/add/1e9,n/3*64*3/mul/1e9);}return 0;}
