/* MIT pilot wrapper around Ropebwt3's MIT rld0 library. Known suffix-table technique. */
#include <stdint.h>
#include <stdlib.h>
#include <stddef.h>
#include "rld0.h"
typedef struct {rld_t *e; int seed; uint64_t *lo,*hi;} idx_t;
static void step(const rld_t *e,int c,int mode,uint64_t*k,uint64_t*l) {
    uint64_t a,b;
    if(mode==0){uint64_t x[6],y[6];rld_rank2a(e,*k,*l,x,y);a=x[c];b=y[c];}
    else rld_rank21(e,*k,*l,c,&a,&b);
    *k=e->cnt[c]+a;*l=e->cnt[c]+b;
}
void *load_index(const char *path,int seed){
    if(seed<0||seed>8)return NULL;
    idx_t*p=calloc(1,sizeof(*p));if(!p)return NULL;p->e=rld_restore(path);p->seed=seed;
    if(!p->e){free(p);return NULL;}
    if(seed){
        size_t n=(size_t)1<<(2*seed);p->lo=calloc(n,8);p->hi=calloc(n,8);
        if(!p->lo||!p->hi){free(p->lo);free(p->hi);rld_destroy(p->e);free(p);return NULL;}
        for(size_t code=0;code<n;code++){
            size_t z=code;uint64_t k=0,l=p->e->cnt[6];
            for(int j=0;j<seed && k<l;j++){step(p->e,1+(z&3),1,&k,&l);z>>=2;}
            p->lo[code]=k;p->hi[code]=l;
        }
    }return p;
}
void close_index(void*v){idx_t*p=v;if(p){rld_destroy(p->e);free(p->lo);free(p->hi);free(p);}}
uint64_t count_one(void*v,const uint8_t*s,int len,int mode){
    idx_t*p=v;if(len<=0)return UINT64_MAX;
    for(int j=0;j<len;j++)if(s[j]<1||s[j]>5)return UINT64_MAX;
    uint64_t k=0,l=p->e->cnt[6];int i=len-1;
    if(p->seed && len>=p->seed){
        size_t code=0;int good=1;
        for(int j=len-p->seed;j<len;j++){if(s[j]>4){good=0;break;}code=(code<<2)|(s[j]-1);}
        if(good){k=p->lo[code];l=p->hi[code];i-=p->seed;}
    }
    for(;i>=0 && k<l;i--)step(p->e,s[i],mode,&k,&l);
    return l-k;
}
uint64_t count_batch(void*v,const uint8_t*seq,const int32_t*offsets,const int32_t*lens,size_t n,int mode,int reps,uint64_t*out){
    uint64_t sum=0;for(int r=0;r<reps;r++)for(size_t i=0;i<n;i++){out[i]=count_one(v,seq+offsets[i],lens[i],mode);sum+=out[i];}return sum;
}
