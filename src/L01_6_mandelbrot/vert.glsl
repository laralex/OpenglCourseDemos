#version 330 core

in vec2 a_position;
in vec2 a_screen_coords;

out vec2 v_screen_coords;

uniform float u_aspect_ratio;
uniform float u_zoom;

void main()
{
   v_screen_coords = a_screen_coords * u_zoom;
   gl_Position = vec4(a_position.x, a_position.y * u_aspect_ratio , 0.0, 1.0);
}