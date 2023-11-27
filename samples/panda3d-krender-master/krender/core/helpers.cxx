#include "krender/core/helpers.h"

#ifdef CPPPARSER  // interrogate
class RPLight;

#else  // normal compiler
#include "internalLightManager.h"
#endif


void print_light_packet(LightPacket* light) {
    printf("LightPacket {\n");
    printf("    slot: %d\n", (int) light->fields.slot);
    printf("    type: ");
    switch ((int) light->fields.type) {
    default:
        printf("LT_empty");
        break;
    case RPLight::LT_point_light:
        printf("LT_point_light");
        break;
    case RPLight::LT_spot_light:
        printf("LT_spot_light");
        break;
    }
    printf("\n");
    printf("    ies: %f\n", light->fields.ies);
    printf("    info: {\n");
    printf("        ss0: %d\n", (int) light->fields.info.fields.ss0);
    printf("        pos: [%f, %f, %f]\n",
           light->fields.info.fields.pos[0],
           light->fields.info.fields.pos[1],
           light->fields.info.fields.pos[2]);
    printf("        color: [%f, %f, %f]\n",
           light->fields.info.fields.color[0],
           light->fields.info.fields.color[1],
           light->fields.info.fields.color[2]);
    printf("        radius: %f\n", light->fields.info.fields.radius);
    printf("        iradius: %f\n", light->fields.iradius);
    printf("    }\n");
    printf("}\n");
}

void print_shadow_source_packet(ShadowSourcePacket* ss) {
    printf("ShadowSourcePacket {\n");
    printf("    slot: %d\n", (int) ss->fields.slot);
    printf("    info: {\n");
    printf("        mvp: [\n");
    for (int i = 0; i < 4 * 4; i += 4) {
        printf("            %f, %f, %f, %f,\n",
               ss->fields.info.fields.mvp[i], ss->fields.info.fields.mvp[i + 1],
               ss->fields.info.fields.mvp[i + 2], ss->fields.info.fields.mvp[i + 3]);
    }
    printf("        ]\n");
    printf("        uv: [%f, %f, %f, %f]\n",
           ss->fields.info.fields.uv[0], ss->fields.info.fields.uv[1],
           ss->fields.info.fields.uv[2], ss->fields.info.fields.uv[3]);
    printf("    }\n");
    printf("}\n");
}
