#version 140

struct Panda3DMaterial {
  vec4 baseColor;
  vec4 emission;
  float roughness;
  float metallic;
  float refractiveIndex;
};

// custom inputs from vertex shader outputs
in vec2 vert_texcoord;
in vec3 vert_normal;
in vec3 vert_position;

uniform Panda3DMaterial p3d_Material;
uniform sampler2D p3d_Texture0;  // ALBEDO

out vec4 color;


void main() {
    vec4 albedo = texture(p3d_Texture0, vert_texcoord);
    if (albedo.a < 0.5) {
        discard;
    }

    color.rgb = albedo.rgb * p3d_Material.baseColor.rgb;
    color.a = 1;
}
