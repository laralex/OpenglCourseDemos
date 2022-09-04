#version 330 core

#define N_CONVERGENCE_STEPS 100
#define THRESHOLD 256.0

precision highp float;
in vec2 v_screen_coords;

out vec4 out_color;

uniform sampler1D u_palette;
uniform vec2 u_center;

vec2 complex_mul(vec2 a, vec2 b) {
      return vec2(a.x*b.x - a.y*b.y, 2*a.x*b.y);
}

void main()
{
      vec2 c = v_screen_coords - u_center;
      vec2 z = c;
      int n_steps = 0;
      while(n_steps < N_CONVERGENCE_STEPS && dot(z,z) < THRESHOLD) {
            z = complex_mul(z,z) + c;
            n_steps += 1;
      }

      float smooth_n_steps = float(n_steps);

      // if (n_steps < N_CONVERGENCE_STEPS) {
      //   float log_zn = log(dot(z,z)) / 2;
      //   float nu = log(log_zn / log(2)) / log(2);
      //   smooth_n_steps += 1.0 - nu;
      // }

      float pallete_coord = (n_steps == N_CONVERGENCE_STEPS ? 0.0 : smooth_n_steps) / N_CONVERGENCE_STEPS;
      out_color = texture1D(u_palette, pallete_coord);
}