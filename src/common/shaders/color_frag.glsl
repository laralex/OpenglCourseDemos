#version 150 core

in vec4 v_custom_data;
out vec4 out_color;

void main()
{
   out_color = v_custom_data;
}