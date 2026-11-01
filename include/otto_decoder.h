#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

// Independent byte-PackBits frames. Validate before writing so malformed input
// cannot partially change the live LVGL canvas. No heap or scratch framebuffer.
inline bool DecodeOttoFrame(const uint8_t* source,size_t size,uint8_t* output,size_t capacity) {
    if(!source || !output || !size || !capacity)return false;
    size_t in=0,out=0;
    while(in<size) {
        const uint8_t command=source[in++];const size_t count=(command&127)+1;
        if(count>capacity-out)return false;
        const size_t consumed=(command&128)?1:count;
        if(consumed>size-in)return false;
        in+=consumed;out+=count;
    }
    if(out!=capacity)return false;
    in=0;out=0;
    while(in<size) {
        const uint8_t command=source[in++];const size_t count=(command&127)+1;
        if(command&128) {std::memset(output+out,source[in++],count);}
        else {std::memcpy(output+out,source+in,count);in+=count;}
        out+=count;
    }
    return true;
}
