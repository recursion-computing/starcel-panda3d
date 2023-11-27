#ifndef CORE_LIGHT_H
#define CORE_LIGHT_H

#include "numeric_types.h"

#include "krender/defines.h"


struct LightInfo_s {
    // written by RPLight
    PN_float32 ss0;  // -1 if not casts shadows
    PN_float32 pos[3];  // vec3
    PN_float32 color[3];  // vec3
    // written by RPPointLight
    PN_float32 radius;
};

union LightInfo {
    struct LightInfo_s fields;
    unsigned char data[LIGHT_INFO_SIZE];
};

struct LightPacket_s {
    // written by LightManager
    PN_float32 slot;
    // written by RPLight
    PN_float32 type;
    PN_float32 ies;
    LightInfo info;
    PN_float32 iradius;
};

union LightPacket {
    struct LightPacket_s fields;
    unsigned char data[LIGHT_PACKET_SIZE];
};

#endif
