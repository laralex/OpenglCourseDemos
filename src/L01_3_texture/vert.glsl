#version 150 core

in vec2 a_position;
in vec2 a_texture_coords;

out vec2 v_texture_coords;

uniform float u_aspect_ratio;

void main()
{
   v_texture_coords = a_texture_coords;
   gl_Position = vec4(a_position.x, a_position.y * u_aspect_ratio , 0.0, 1.0);
}