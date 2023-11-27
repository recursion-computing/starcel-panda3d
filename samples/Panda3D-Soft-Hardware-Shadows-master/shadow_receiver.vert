//Shaders adapted from examples by @wezu:
//https://discourse.panda3d.org/t/shadows-made-easy/15399
#version 330

uniform struct p3d_LightSourceParameters {
    // Primary light color.
    vec4 color;

    // Light color broken up into components, for compatibility with legacy
    // shaders.  These are now deprecated.
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;

    // View-space position.  If w=0, this is a directional light, with the xyz
    // being -direction.
    vec4 position;

    // Spotlight-only settings
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;

    // Individual attenuation constants
    float constantAttenuation;
    float linearAttenuation;
    float quadraticAttenuation;

    // constant, linear, quadratic attenuation in one vector
    vec3 attenuation;

    // Shadow map for this light source
    // ENABLE FOR HARD SHADOWS:
    //samplerCube shadowMap;

    // ENABLE FOR SOFT SHADOWS:
    samplerCubeShadow shadowMap;

    // Transforms view-space coordinates to shadow map coordinates
    mat4 shadowViewMatrix;
} p3d_LightSource[1];

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec2 uv;
out vec4 shadow_uv;
out vec3 normal;

out vec3 vertex_viewspace;
out vec3 normal_viewspace;

void main()
    {
    //position    
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;      
    //normal      
    normal = p3d_NormalMatrix * p3d_Normal;
    //uv
    uv = p3d_MultiTexCoord0;

    normal_viewspace = normalize( p3d_NormalMatrix * p3d_Normal );
    vertex_viewspace = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    //shadows
    //shadow_uv = p3d_LightSource[0].shadowViewMatrix * p3d_Vertex;
    shadow_uv = p3d_LightSource[0].shadowViewMatrix * vec4(vertex_viewspace, 1);
    //shadow_uv = p3d_LightSource[0].shadowViewMatrix * (p3d_ModelViewMatrix * p3d_Vertex);

}


