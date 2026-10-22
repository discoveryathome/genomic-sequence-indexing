// Pilot-owned adapter. The locally linked SDSL library is GPLv3; no binary is shipped.
#include <sdsl/suffix_arrays.hpp>
#include <sdsl/wavelet_trees.hpp>
#include <string>
#include <cstdint>
using Index=sdsl::csa_wt<sdsl::wt_huff<sdsl::rrr_vector<63>>,32,64>;
extern "C" {
int fm_build(const uint8_t* data, size_t n, const char* path) {
    try {Index index; sdsl::construct_im(index,std::string((const char*)data,n),1);
         return sdsl::store_to_file(index,path)?0:1;} catch(...) {return 2;}
}
void* fm_load(const char* path) {
    try {auto* p=new Index; if(!sdsl::load_from_file(*p,path)){delete p;return nullptr;}return p;}
    catch(...) {return nullptr;}
}
void fm_close(void* p) {delete static_cast<Index*>(p);}
uint64_t fm_batch(void* p,const uint8_t* data,const int32_t* offsets,const int32_t* lengths,
                  size_t n,int reps,uint64_t* out) {
    auto& index=*static_cast<Index*>(p); uint64_t total=0;
    for(int r=0;r<reps;++r) for(size_t i=0;i<n;++i) {
        out[i]=sdsl::count(index,data+offsets[i],data+offsets[i]+lengths[i]);total+=out[i];
    }
    return total;
}
}
