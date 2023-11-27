#version 140
// version 140, so we can use sampler2D

#pragma include "krender/shader/blur.inc.frag.glsl"

// custom inputs from the first render pass
uniform sampler2D base_emissive;

// custom inputs from the previous render pass
uniform sampler2D prev_color;

// custom inputs from vertex shader outputs
in vec2 vert_uv;

// outputs
out vec4 color;


void main() {
    vec3 bloom = process_blur(base_emissive, vert_uv);

    color = texture(prev_color, vert_uv);
    color.rgb += bloom.rgb;
    color.a = 1.0;
}
