#version 130
// https://docs.panda3d.org/1.10/python/programming/shaders/list-of-glsl-inputs

// base panda inputs
in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Normal;
in vec4 p3d_Tangent;
in vec4 p3d_Vertex;

// uniform panda inputs
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewProjectionMatrix;

// custom outputs to fragment shader
out vec2 vert_uv;
out vec3 vert_norm;
out vec3 vert_pos;
out vec3 vert_tan;
out vec3 vert_binorm;


void main() {
    vert_uv = p3d_MultiTexCoord0;

    vec4 vertex = p3d_Vertex;
    mat4 model_matrix = p3d_ModelMatrix;

    vert_pos = (model_matrix * vertex).xyz;
    vert_norm = normalize(model_matrix * vec4(p3d_Normal.xyz, 0.0)).xyz;

    // calculate TBN vectors using precomputed vec4 tangent
    // https://community.khronos.org/t/bones-and-normals-binormals-tangent/40598/4
    // http://fabiensanglard.net/bumpMapping/index.php
    vert_tan = normalize(model_matrix * vec4(p3d_Tangent.xyz, 0.0)).xyz;
    vert_binorm = normalize(cross(vert_norm, vert_tan) * p3d_Tangent.w);

    gl_Position = p3d_ViewProjectionMatrix * vec4(vert_pos, 1.0);
}
