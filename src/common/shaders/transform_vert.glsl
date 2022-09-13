#version 150 core

in vec4 a_position;
in vec4 a_custom_data;

out vec4 v_custom_data;

uniform float u_aspect_ratio;
uniform mat4 u_transform;

void main()
{
   v_custom_data = a_custom_data;
   gl_Position = u_transform * a_position;
   gl_Position.y *= u_aspect_ratio;
}