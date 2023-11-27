#version 130
// version 130, so we can drop gl_FragColor
// https://docs.panda3d.org/1.10/python/programming/shaders/list-of-glsl-inputs

#pragma include ".krender_config.inc.glsl"

// fragment shader input
#if (DEPTH2COLOR == 1)
    in vec4 vert_pos;
#endif

// fragment shader output
#if (DEPTH2COLOR == 1)
    out vec4 color;
#endif


void main() {
    // empty shader by default, because we render depth only (in vertex shader)
#if (DEPTH2COLOR == 1)
    float z = (vert_pos.z / vert_pos.w) * 0.5 + 0.5;
    color = vec4(z, 0, 0, 1);
#endif
}
