#pragma include ".krender_config.inc.glsl"
#pragma include "krender/shader/defines.inc.glsl"

#define SHADOW_BIAS 0.01
#define SHADOW_BIAS_PCF 0.005

#if (SUPPORTS_SHADOW_FILTER == 1)
#define SHADOWMAP sampler2DShadow
#else
#define SHADOWMAP sampler2D
#endif

#ifndef LIGHT_MODEL
#define LIGHT_MODEL lambert
#endif

#ifndef LIGHT_ATTENUATION
#define LIGHT_ATTENUATION linear_attenuation
#endif

#ifndef SHADING_DATA
#define SHADING_DATA ShadingData
#endif

struct ShadingData {
    vec3 vert_pos;
    vec3 normal;
};

float lambert(SHADING_DATA shading_data, vec3 l) {
    /*
      Lambert light calculation.
     */
    float NxL = dot(shading_data.normal, l);
    return max(NxL, 0.0);
}

float linear_attenuation(float light_radius, float light_dist) {
    /*
      Light attenuation.
     */
    // 1 - edge of light radius, 0 - center of light
    float range = min(light_dist / light_radius, 1.0);
    return 1.0 - range;
}

int get_ss_slot(vec3 dir) {
    /*
      Get the affected by direction Shadow Source slot of the specific light.
    */
    vec3 dir_abs = abs(dir);
    float axis_max = max(max(dir_abs.x, dir_abs.y), dir_abs.z);
    if (dir_abs.x >= axis_max - 0.00001) return dir.x >= 0.0 ? 0 : 1;
    if (dir_abs.y >= axis_max - 0.00001) return dir.y >= 0.0 ? 2 : 3;
    return dir.z >= 0.0 ? 4 : 5;
}

float process_shadow(samplerBuffer light_data, SHADOWMAP shadowmap, SHADING_DATA shading_data, int ss0_slot, vec3 light_vec, float light_dist) {
    /*
      https://learnopengl.com/Advanced-Lighting/Shadows/Shadow-Mapping
    */
#if (SUPPORTS_SHADOW_FILTER == 1)
    float bias = SHADOW_BIAS_PCF;
#else
    float bias = SHADOW_BIAS;
#endif

    // find a single Shadow Source slot to process
    int ss_slot = ss0_slot + get_ss_slot(-light_vec);
    int index = ((LIGHT_INFO_SIZE * MAX_LIGHTS) + (SHADOW_SOURCE_INFO_SIZE * ss_slot)) / RGBA32;
    vec4 ss_mvp0 = texelFetch(light_data, index++);
    vec4 ss_mvp1 = texelFetch(light_data, index++);
    vec4 ss_mvp2 = texelFetch(light_data, index++);
    vec4 ss_mvp3 = texelFetch(light_data, index++);
    vec4 ss_uv = texelFetch(light_data, index++);
    mat4 ss_mvp = mat4(ss_mvp0, ss_mvp1, ss_mvp2, ss_mvp3);

    // light-space fragment position
    vec4 light_clip = ss_mvp * vec4(shading_data.vert_pos, 1.0);

    // perform perspective divide
    vec3 shadow_uv = light_clip.xyz / light_clip.w;

    // transform to 0...1 range
    shadow_uv = shadow_uv * 0.5 + 0.5;

    // get tile UV on shadowmap atlas
    vec3 tile_uv = vec3(shadow_uv.xy * ss_uv.zw + ss_uv.xy, shadow_uv.z - bias);

    vec2 texel_size = 1.0 / textureSize(shadowmap, 0);

    float light_shadow = 0.0;
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
            vec3 off_uv = vec3(x, y, 0.0) * vec3(texel_size, 0.0);

#if (SUPPORTS_SHADOW_FILTER == 1)
            light_shadow += texture(shadowmap, tile_uv + off_uv);
#else
            // get closest depth value from light's perspective (using 0...1 range)
            float ray_length = texture(shadowmap, tile_uv.xy + off_uv.xy).x;

            // light ray penetration depth
            // the deeper it goes inside - the darker the shadows become
            float depth = max(tile_uv.z - ray_length, 0.0);

            light_shadow += (depth > bias) ? 0.0 : 1.0;
#endif
        }
    }

    return clamp(light_shadow / 9.0, 0.0, 1.0);
}

vec4 process_light(samplerBuffer light_data, SHADOWMAP shadowmap, SHADING_DATA shading_data, int light_slot) {
    // load and parse data
    int index = LIGHT_INFO_SIZE * light_slot / RGBA32;
    vec4 lights1 = texelFetch(light_data, index + 1);
    vec3 light_col = lights1.rgb;
    float light_radius = lights1.a;

    if (light_radius == 0) return vec4(0.0);

    vec4 lights0 = texelFetch(light_data, index + 0);
    int ss0_slot = int(lights0.x);
    vec3 light_pos = lights0.yzw;

    // prepare input values
    vec3 light_vec = normalize(light_pos - shading_data.vert_pos);
    float light_dist = distance(light_pos, shading_data.vert_pos);

    // calculate lights and shadows
    float light_power = LIGHT_MODEL(shading_data, light_vec);
    float light_attenuation = LIGHT_ATTENUATION(light_radius, light_dist);
    float light_shadow = 1;
    if (ss0_slot >= 0 && light_power >= 0.001) {
        light_shadow = process_shadow(light_data, shadowmap, shading_data, ss0_slot, light_vec, light_dist);
    }

    // colorize
    float lightness = light_power * light_attenuation * light_shadow;
    return vec4(light_col * lightness, lightness);
}

vec4 process_shading(samplerBuffer light_data, SHADOWMAP shadowmap, SHADING_DATA shading_data) {
    vec4 shading = vec4(0.0, 0.0, 0.0, 0.0);
    int lights = 0;
    for (int light_slot = 0; light_slot < MAX_LIGHTS; light_slot++) {
        vec4 light_shading = process_light(light_data, shadowmap, shading_data, light_slot);
        shading += light_shading;

        if (light_shading.a >= 0.001) lights++;
        if (lights >= 2) break;
    }
    return shading;
}
