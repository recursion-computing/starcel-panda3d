#pragma include ".krender_config.inc.glsl"
#pragma include "krender/shader/defines.inc.glsl"


vec3 decode_normal(vec3 color) {
    /*
      Convert 0...1 colors values to -1...1 normal values.
      RGB Color -> XYZ Normal
    */
    return color * 2.0 - 1.0;
}

vec3 encode_normal(vec3 normal) {
    /*
      Convert -1...1 normal values to 0...1 color values.
      XYZ Normal -> RGB Color
    */
    return normal / 2.0 + 0.5;
}

float lrgb(float x) {
    /*
      sRGB to Linear RGB, single channel.
     */
    return (
        (x <= 0.04045) ?
        x / 12.92 :
        pow((x + 0.055) / (1.0 + 0.055), 2.4));
}

float srgb(float x) {
    /*
      Linear RGB to sRGB, single channel.
    */
#if (SRGB_COLOR == 1)
    return x;
#else
    return (
        (x <= 0.0031308) ?
        12.92 * x :
        ((1.0 + 0.055) * pow(x, 1.0 / 2.4) - 0.055));
#endif
}

vec3 lrgb3(vec3 srgb_color) {
    /*
      sRGB to Linear RGB.
    */
    return vec3(
        lrgb(srgb_color.r),
        lrgb(srgb_color.g),
        lrgb(srgb_color.b));
}

vec3 srgb3(vec3 lrgb_color) {
    /*
      Linear RGB to sRGB.
    */
    return vec3(
        srgb(lrgb_color.r),
        srgb(lrgb_color.g),
        srgb(lrgb_color.b));
}
