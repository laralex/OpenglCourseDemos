#version 330 core

layout(location=1) in vec2 a_texture_coords;
in vec3 a_position;

uniform float u_aspect_ratio;

void main()
{
   gl_Position = vec4(a_texture_coords-0.5, -1.0, 1.0);
   gl_Position.y *= u_aspect_ratio;
}