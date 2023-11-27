#version 140
// version 140 for samplerBuffer
// https://docs.panda3d.org/1.10/python/programming/shaders/list-of-glsl-inputs

#pragma include "krender/shader/base.inc.frag.glsl"
#pragma include "krender/shader/shading.inc.frag.glsl"

// panda structs
struct Panda3DMaterial {
    vec4 baseColor;
    vec4 emission;
};

// panda inputs
uniform Panda3DMaterial p3d_Material;
uniform sampler2D p3d_TextureModulate;
uniform sampler2D p3d_TextureNormal;
uniform sampler2D p3d_TextureEmission;

// custom inputs from vertex shader outputs
in vec2 vert_uv;
in vec3 vert_norm;
in vec3 vert_pos;
in vec3 vert_tan;
in vec3 vert_binorm;

// custom inputs
uniform samplerBuffer light_data;
#if (SUPPORTS_SHADOW_FILTER == 1)
    uniform sampler2DShadow shadowmap;
#else
    uniform sampler2D shadowmap;
#endif

// outputs
out vec4 color;
out vec4 emissive;


void main() {
    mat3 tbn = mat3(vert_tan, vert_binorm, vert_norm);
    vec4 diffuse = texture(p3d_TextureModulate, vert_uv);
    vec4 normal_map = texture(p3d_TextureNormal, vert_uv);
    vec3 normal = normalize(tbn * normalize(decode_normal(normal_map.rgb))).xyz;
    vec4 emission_map = texture(p3d_TextureEmission, vert_uv);
    vec3 emission = emission_map.rgb * p3d_Material.emission.rgb;

    emissive.rgb = diffuse.rgb * emission.rgb;
    emissive.a = diffuse.a;

    ShadingData shading_data;
    shading_data.vert_pos = vert_pos;
    shading_data.normal = normal;
    vec4 shading = process_shading(light_data, shadowmap, shading_data);
    shading += min(emissive.r + emissive.g + emissive.b, 1.0);

    color.rgb = diffuse.rgb * p3d_Material.baseColor.rgb * shading.rgb;
    color.rgb = srgb3(color.rgb);
    color.a = diffuse.a;
}
