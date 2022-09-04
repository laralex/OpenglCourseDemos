#version 150 core

in vec2 a_position;
in vec2 a_texture_coords;

out vec2 v_texture_coords;

uniform float u_aspect_ratio;

// === CHANGE #1
uniform mat3 u_transform;

void main()
{
   v_texture_coords = a_texture_coords;

   // === CHANGE #2
   vec3 screen_position = u_transform * vec3(a_position, 1.0);
   gl_Position = vec4(screen_position.x, screen_position.y * u_aspect_ratio , screen_position.z, 1.0);
}