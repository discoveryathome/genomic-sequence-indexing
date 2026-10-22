/* MIT pilot binary-search count control, built with Apache-2.0 libsais.
 * Full uncompressed suffix array; not a production compressed-index baseline. */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "libsais.h"
typedef struct { uint8_t *text; int32_t *sa; int32_t n; } sa_index;
void sa_close(void *v) {
    sa_index *p=v;
    if(p) { free(p->text); free(p->sa); free(p); }
}
int sa_build(const uint8_t *text, int32_t n, const char *file) {
    if(n<=0) return -1;
    int32_t *sa=malloc((size_t)n*sizeof(int32_t));
    if(!sa) return -1;
    if(libsais(text,sa,n,0,NULL)<0) { free(sa); return -1; }
    FILE *f=fopen(file,"wb");
    if(!f) { free(sa); return -1; }
    uint64_t head[2]={0x444148534131ULL,(uint64_t)n};
    int ok=fwrite(head,8,2,f)==2 && fwrite(text,1,n,f)==(size_t)n &&
           fwrite(sa,4,n,f)==(size_t)n;
    if(fclose(f)) ok=0;
    free(sa); return ok?0:-1;
}
void *sa_load(const char *file) {
    FILE *f=fopen(file,"rb");
    if(!f) return NULL;
    uint64_t head[2];
    if(fread(head,8,2,f)!=2 || head[0]!=0x444148534131ULL || head[1]==0 || head[1]>INT32_MAX) { fclose(f); return NULL; }
    sa_index *p=calloc(1,sizeof(*p));
    if(!p) { fclose(f); return NULL; }
    p->n=(int32_t)head[1]; p->text=malloc(p->n); p->sa=malloc((size_t)p->n*4);
    int ok=p->text && p->sa;
    if(ok) ok=fread(p->text,1,p->n,f)==(size_t)p->n && fread(p->sa,4,p->n,f)==(size_t)p->n && fgetc(f)==EOF;
    if(ok) for(int32_t i=0;i<p->n;i++) if(p->sa[i]<0 || p->sa[i]>=p->n) { ok=0; break; }
    fclose(f); if(!ok) { sa_close(p); return NULL; } return p;
}
static int compare(sa_index *p,int32_t pos,const uint8_t *q,int len) {
    int avail=p->n-pos, n=avail<len?avail:len;
    int c=memcmp(p->text+pos,q,n);
    return c?c:(avail<len?-1:0);
}
uint64_t sa_count(void *v,const uint8_t *q,int len) {
    sa_index *p=v;
    if(len<=0) return UINT64_MAX;
    for(int i=0;i<len;i++) if(q[i]<1 || q[i]>5) return UINT64_MAX;
    int32_t lo=0,hi=p->n;
    while(lo<hi) { int32_t mid=lo+(hi-lo)/2; if(compare(p,p->sa[mid],q,len)<0)lo=mid+1;else hi=mid; }
    int32_t first=lo; hi=p->n;
    while(lo<hi) { int32_t mid=lo+(hi-lo)/2; if(compare(p,p->sa[mid],q,len)<=0)lo=mid+1;else hi=mid; }
    return (uint64_t)(lo-first);
}
uint64_t sa_batch(void *v,const uint8_t *seq,const int32_t *offsets,const int32_t *lens,size_t n,int reps,uint64_t *out) {
    uint64_t sum=0;
    for(int r=0;r<reps;r++)for(size_t i=0;i<n;i++) { out[i]=sa_count(v,seq+offsets[i],lens[i]);sum+=out[i]; }
    return sum;
}
