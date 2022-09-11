#version 150 core
in vec2 v_texture_coords;

out vec4 out_color;

uniform sampler2D u_texture;

void main()
{
      out_color = texture(u_texture, v_texture_coords) + vec4(0.0, 0.3, 0.0, 0.0);
}