#version 130
// https://docs.panda3d.org/1.10/python/programming/shaders/list-of-glsl-inputs

// base panda inputs
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;

// uniform panda inputs
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewProjectionMatrix;

// custom outputs to fragment shader
out vec2 vert_uv;


void main() {
    vert_uv = p3d_MultiTexCoord0;

    vec4 vertex = p3d_Vertex;
    mat4 model_matrix = p3d_ModelMatrix;

    gl_Position = p3d_ViewProjectionMatrix * model_matrix * vertex;
}
