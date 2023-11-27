#version 130
// https://docs.panda3d.org/1.10/python/programming/shaders/list-of-glsl-inputs

#define DEPTH2COLOR 0

// base panda inputs
in vec4 p3d_Vertex;

// uniform panda inputs
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewProjectionMatrix;

// vertex shader outputs
#if (DEPTH2COLOR == 1)
    out vec4 vert_pos;
#endif


void main() {
    vec4 vertex = p3d_Vertex;
    mat4 model_matrix = p3d_ModelMatrix;

#if (DEPTH2COLOR == 1)
    vert_pos = p3d_ViewProjectionMatrix * model_matrix * vertex;
    gl_Position = vert_pos;

#else
    gl_Position = p3d_ViewProjectionMatrix * model_matrix * vertex;

#endif
}
