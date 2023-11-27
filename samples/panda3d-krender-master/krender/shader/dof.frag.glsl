#version 140
// version 140, so we can use sampler2D

#pragma include "krender/shader/blur.inc.frag.glsl"

// custom inputs from the first render pass
uniform sampler2D base_depth;

// custom inputs from the previous render pass
uniform sampler2D prev_color;

// custom inputs
uniform float dof_focus_near;
uniform float dof_focus_far;
uniform float dof_blur_near;
uniform float dof_blur_far;

// custom inputs from vertex shader outputs
in vec2 vert_uv;

// outputs
out vec4 color;


float get_z_from_depth(float depth) {
    // convert 0...1 depth values to -1...1 depth values.
    float depth_decoded = (depth * 2.0 - 1.0);

    float cam_depth_range = CAM_FAR - CAM_NEAR;
    float cam_depth_max = CAM_FAR + CAM_NEAR;
    return (
        2.0 * CAM_NEAR * CAM_FAR /
        (cam_depth_max - depth_decoded * cam_depth_range));
}

void main() {
    float depth = texture(base_depth, vert_uv).x;
    float z = get_z_from_depth(depth);

    float dof_focus = dof_focus_far - dof_focus_near;
    float dof_focus_mid = dof_focus_near + dof_focus / 2.0;
    float value = (
        z > dof_focus_mid ?
        smoothstep(dof_focus_far, dof_blur_far, z) :
        (1.0 - smoothstep(dof_blur_near, dof_focus_near, z)));

    vec3 focus = texture(prev_color, vert_uv).rgb;
    vec3 blur = process_blur(prev_color, vert_uv);

    color.rgb = mix(focus, blur, value);
    color.a = 1.0;
}
