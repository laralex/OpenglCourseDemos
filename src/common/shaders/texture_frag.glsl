#version 150 core

in vec4 v_custom_data;
out vec4 out_color;
uniform sampler2D u_texture;

void main()
{
   out_color = texture(u_texture, v_custom_data.xy);
}