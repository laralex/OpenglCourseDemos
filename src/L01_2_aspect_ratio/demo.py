import numpy as np
from ..demos_loader import Demo
from ..common.defines import *
from OpenGL.GL import *

class Lecture01_AspectRatioDemo(Demo):
    def __init__(self):
        super().__init__(ui_defaults=None)

    def load(self, window):
        self.make_shader()
        self.make_vertex_data()
        self.is_loaded = True

    def make_shader(self):
        # GLSL code
        vertex_shader_code = """
            #version 150 core
            in vec2 a_position;
            in vec3 a_color;

            out vec3 v_color;

            // === CHANGE #1
            uniform float u_aspect_ratio;
            // e.g. screen 800x600 px, aspect ratio 800/600 = 1.333

            void main()
            {
                v_color = a_color;
                // gl_Position = vec4(a_position.x, a_position.y                 , 0.0, 1.0);
                // === CHANGE #2
                gl_Position    = vec4(a_position.x, a_position.y * u_aspect_ratio, 0.0, 1.0);
            }
        """

        fragment_shader_code = """
            #version 150 core
            in vec3 v_color;

            out vec3 out_color;

            void main()
            {
                out_color = v_color;
            }
        """

        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, vertex_shader_code)
        glCompileShader(self.vertex_shader)

        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, fragment_shader_code)
        glCompileShader(self.fragment_shader)

        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vertex_shader)
        glAttachShader(self.shader_program, self.fragment_shader)

        glBindFragDataLocation(self.shader_program, 0, b"out_color")

        glLinkProgram(self.shader_program)

        self.check_shader_compilation()


    def check_shader_compilation(self):
        if not glGetShaderiv(self.vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(self.vertex_shader)
            raise Exception(f"Vertex shader didn't compile with error: {error}")
        if not glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(self.fragment_shader)
            raise Exception(f"Fragment shader didn't compile with error: {error}")
        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.shader_program)
            raise Exception(f"Shader program didn't compile with error: {error}")

    def make_vertex_data(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        glUseProgram(self.shader_program)

        positions = np.array((
            # X     Y
             0.0,  0.5,
             0.5, -0.5,
            -0.5, -0.5,
        ), dtype=np.float32, order='C')

        float_nbytes = positions.itemsize # 4

        colors = np.array((
            # R    G    B
             1.0, 0.0, 0.0,
             0.0, 1.0, 0.0,
             0.0, 0.0, 1.0,
        ), dtype=np.float32, order='C')

        # send data to GPU
        self.gpu_positions, self.gpu_colors = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_positions)
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        position_attribute = glGetAttribLocation(self.shader_program, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            2, # how many values (1-4) to read after jump
            GL_FLOAT, # 4 bytes per value
            GL_FALSE, # no normalization
            2*float_nbytes, # stride (jump size in bytes when iterating data)
            None # offset in the data
        )

        # same for colors
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_colors)
        glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)

        color_attribute = glGetAttribLocation(self.shader_program, "a_color")
        glEnableVertexAttribArray(color_attribute)
        glVertexAttribPointer(color_attribute,
            3,
            GL_FLOAT,
            GL_FALSE,
            3*float_nbytes,
            None)


    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT)

        # use shader and vertex data to draw triangles
        glUseProgram(self.shader_program)

        # === CHANGE #3
        uniform_aspect = glGetUniformLocation(self.shader_program, "u_aspect_ratio")
        glUniform1f(uniform_aspect, width / height) 
        # ===

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)

    def unload(self):
        if not self.is_loaded:
            return

        glDeleteVertexArrays(1, np.asarray([self.vao]))
        glDeleteBuffers(2, np.asarray([self.gpu_positions, self.gpu_colors]))
        glDeleteProgram(self.shader_program)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)
        del self.gpu_positions, self.gpu_colors
        del self.shader_program, self.vertex_shader, self.fragment_shader
        super().unload()


