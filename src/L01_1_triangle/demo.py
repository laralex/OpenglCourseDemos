from dataclasses import dataclass
import numpy as np
import glfw
from ..all_demos import Demo
from ..common.defines import *
from OpenGL.GL import *

@dataclass
class UiDefaults:
    color: int

class Lecture01_TriangleDemo(Demo):
    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def load(self, window):
        self.draw_mode = GL_TRIANGLES
        self.make_shader()
        self.make_vertex_data()
        self.is_loaded = True

    def make_shader(self):
        vertex_shader_code = """
            #version 150 core
            in vec2 a_position;
            in vec3 a_color;

            out vec3 v_color;

            void main()
            {
                v_color = a_color;
                gl_Position = vec4(a_position, 0.0, 1.0);
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
             0.0,  0.5,
             0.5, -0.5,
            -0.5, -0.5,
        ), dtype=np.float32, order='C')

        float_nbytes = positions.itemsize # 4

        colors = np.array((
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
        glBindVertexArray(self.vao)
        glDrawArrays(self.draw_mode, 0, 3)

    def keyboard_callback(self, window, key, scancode, action, mods):
        if (key, action) == (glfw.KEY_T, glfw.PRESS):
            if self.draw_mode == GL_TRIANGLES:
                self.draw_mode = GL_LINE_LOOP
            else:
                self.draw_mode = GL_TRIANGLES
        return super().keyboard_callback(window, key, scancode, action, mods)

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


