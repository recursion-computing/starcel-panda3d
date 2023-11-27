#ifndef CORE_SHADOW_SOURCE_H
#define CORE_SHADOW_SOURCE_H

#include "numeric_types.h"

#include "krender/defines.h"


struct ShadowSourceInfo_s {
    // written by ShadowSource
    PN_float32 mvp[4 * 4];  // mat4
    PN_float32 uv[4];  // vec4
};

union ShadowSourceInfo {
    struct ShadowSourceInfo_s fields;
    unsigned char data[SHADOW_SOURCE_INFO_SIZE];
};

struct ShadowSourcePacket_s {
    // written by LightManager
    PN_float32 slot;
    ShadowSourceInfo info;
};

union ShadowSourcePacket {
    struct ShadowSourcePacket_s fields;
    unsigned char data[SHADOW_SOURCE_PACKET_SIZE];
};

#endif
