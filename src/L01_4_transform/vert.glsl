#version 150 core

in vec2 a_position;
in vec2 a_texture_coords;

out vec2 v_texture_coords;

uniform float u_aspect_ratio;

// === CHANGE #1
uniform mat2 u_transform;
uniform vec2 u_translation;

void main()
{
   v_texture_coords = a_texture_coords;
   
   // === CHANGE #2
   vec2 screen_position = u_transform * a_position + u_translation;
   gl_Position = vec4(screen_position.x, screen_position.y * u_aspect_ratio , 0.0, 1.0);
}