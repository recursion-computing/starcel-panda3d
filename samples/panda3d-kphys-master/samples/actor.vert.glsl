#version 140

in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Normal;
in vec4 p3d_Vertex;

// GPU skinning inputs, bone index and weight for 4 bones
in vec4 transform_weight;
in uvec4 transform_index;
uniform samplerBuffer bone_transform_tex;

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ViewProjectionMatrix;

// custom outputs to fragment shader
out vec2 vert_texcoord;
out vec3 vert_normal;
out vec3 vert_position;


mat4 get_transform_matrix(int bone_id) {
    int index = bone_id * 4;
    vec4 row0 = texelFetch(bone_transform_tex, index);
    vec4 row1 = texelFetch(bone_transform_tex, index + 1);
    vec4 row2 = texelFetch(bone_transform_tex, index + 2);
    vec4 row3 = texelFetch(bone_transform_tex, index + 3);
    return mat4(row0, row1, row2, row3);
}

void main() {
    vert_texcoord = p3d_MultiTexCoord0;

    vec4 vertex_position = p3d_Vertex;
    mat4 model_matrix = p3d_ModelMatrix;

    // GPU skinning
    mat4 skin_matrix = (
        get_transform_matrix(int(transform_index.x)) * transform_weight.x +
        get_transform_matrix(int(transform_index.y)) * transform_weight.y +
        get_transform_matrix(int(transform_index.z)) * transform_weight.z +
        get_transform_matrix(int(transform_index.w)) * transform_weight.w);
    model_matrix *= skin_matrix;

    vert_normal = normalize(model_matrix * vec4(p3d_Normal.xyz, 0)).xyz;
    vert_position = (model_matrix * vertex_position).xyz;

    gl_Position = p3d_ViewProjectionMatrix * vec4(vert_position, 1);
}
