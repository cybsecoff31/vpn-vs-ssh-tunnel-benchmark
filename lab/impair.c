// impair.c - userspace link emulator between two TUN devices.
// Applies independent Bernoulli loss and fixed one-way delay per direction.
// Usage: impair <tunA> <tunB> <loss_prob> <delay_ms> <seed>
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <poll.h>
#include <time.h>
#include <sys/ioctl.h>
#include <linux/if.h>
#include <linux/if_tun.h>
#define QCAP 65536
#define PMAX 2048
typedef struct { int len; long long due; unsigned char buf[PMAX]; } pkt_t;
typedef struct { int in, out; double loss; long long delay_ns; unsigned int seed; pkt_t *q; } dir_t;
static long long now_ns(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec*1000000000LL+t.tv_nsec; }
static int tun_open(const char *name){
  int fd=open("/dev/net/tun",O_RDWR); if(fd<0){perror("open");exit(1);}
  struct ifreq ifr; memset(&ifr,0,sizeof ifr); ifr.ifr_flags=IFF_TUN|IFF_NO_PI;
  strncpy(ifr.ifr_name,name,IFNAMSIZ-1);
  if(ioctl(fd,TUNSETIFF,&ifr)<0){perror("TUNSETIFF");exit(1);} return fd; }
static void *run(void *a){
  dir_t *d=a; int head=0, tail=0;
  for(;;){
    int timeout=-1;
    if(head!=tail){ long long w=d->q[head].due-now_ns(); timeout = w<=0?0:(int)(w/1000000)+0; if(w>0 && timeout==0) timeout=1; }
    struct pollfd p={d->in,POLLIN,0};
    int r=poll(&p,1,timeout);
    if(r>0 && (p.revents&POLLIN)){
      for(int k=0;k<64;k++){ // drain burst
        int nt=(tail+1)%QCAP; if(nt==head) break;
        int n=read(d->in,d->q[tail].buf,PMAX); if(n<=0) break;
        if(d->loss>0 && (double)rand_r(&d->seed)/RAND_MAX < d->loss) continue;
        d->q[tail].len=n; d->q[tail].due=now_ns()+d->delay_ns; tail=nt;
        struct pollfd p2={d->in,POLLIN,0}; if(poll(&p2,1,0)<=0) break;
      }
    }
    long long t=now_ns();
    while(head!=tail && d->q[head].due<=t){ (void)!write(d->out,d->q[head].buf,d->q[head].len); head=(head+1)%QCAP; }
  }
  return 0; }
int main(int c,char**v){
  if(c<6){fprintf(stderr,"usage\n");return 1;}
  int a=tun_open(v[1]), b=tun_open(v[2]); double loss=atof(v[3]); long long dn=(long long)(atof(v[4])*1e6); unsigned s=atoi(v[5]);
  dir_t ab={a,b,loss,dn,s,calloc(QCAP,sizeof(pkt_t))}, ba={b,a,loss,dn,s*7919u+1,calloc(QCAP,sizeof(pkt_t))};
  pthread_t t1,t2; pthread_create(&t1,0,run,&ab); pthread_create(&t2,0,run,&ba); pthread_join(t1,0); return 0; }
