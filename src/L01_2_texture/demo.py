from dataclasses import dataclass
from pickle import FALSE
from typing import overload
from ..common import parse_json, window
from ..common.gl_texture import GpuTexture
from ..all_demos import Demo
from OpenGL.GL import *
from PIL import Image
import sys
import numpy as np

@dataclass
class UiDefaults:
    color: int

class Lecture01_TextureDemo(Demo):
    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def load(self, window):
        super().load(window)
        self.make_shader()
        self.make_vertex_data()
        self.make_fragment_data()
        self.is_loaded = True

    def make_shader(self):
        vertex_shader_code = """
            #version 150 core
            in vec2 a_position;
            in vec2 a_texcoord;

            out vec2 v_texcoord;

            void main()
            {
                v_texcoord = a_texcoord;
                gl_Position = vec4(a_position, 1.0, 1.0);
            }
        """

        fragment_shader_code = """
            #version 150 core
            in vec2 v_texcoord;

            out vec4 out_color;

            uniform sampler2D color_texture;

            void main()
            {
                out_color = texture(color_texture, v_texcoord);
            }
        """

        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, [vertex_shader_code])
        glCompileShader(self.vertex_shader)

        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, [fragment_shader_code])
        glCompileShader(self.fragment_shader)

        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vertex_shader)
        glAttachShader(self.shader_program, self.fragment_shader)

        glBindFragDataLocation(self.shader_program, 0, "out_color")

        glLinkProgram(self.shader_program)

        self.check_shader_compilation()


    def check_shader_compilation(self):
        vertex_compilation_log   = glGetShaderInfoLog(self.vertex_shader)
        fragment_compilation_log = glGetShaderInfoLog(self.fragment_shader)
        shader_linking_log       = glGetProgramInfoLog(self.shader_program)
        if vertex_compilation_log != "":
            raise Exception(f"Vertex shader didn't compile with error: {vertex_compilation_log}")
        if fragment_compilation_log != "":
            raise Exception(f"Fragment shader didn't compile with error: {fragment_compilation_log}")
        if shader_linking_log != "":
            raise Exception(f"Shader program didn't compile with error: {shader_linking_log}")

    def make_vertex_data(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        vertices = np.ascontiguousarray([
            -0.5,  0.5,  0.0,  0.0,
             0.0,  0.0,  1.0,  0.0,
             0.5, -0.5,  1.0,  1.0,
            -0.5, -0.5,  0.0,  1.0
        ], dtype=np.float32)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glUseProgram(self.shader_program)

        float_size = vertices.itemsize
        vertices_stride_bytes = 4*float_size
        position_attribute = glGetAttribLocation(self.shader_program, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute, 2, GL_FLOAT, GL_FALSE,
                            vertices_stride_bytes, 0)

        tex_coord_attribute = glGetAttribLocation(self.shader_program, "a_texcoord")
        glEnableVertexAttribArray(tex_coord_attribute);
        glVertexAttribPointer(tex_coord_attribute, 2, GL_FLOAT, GL_FALSE,
                            vertices_stride_bytes, 2*float_size)

        # index array
        indices = np.ascontiguousarray([
             0, 1, 3,
             1, 2, 3,
        ], dtype=np.int32)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glBindVertexArray(0)


    def make_fragment_data(self):
        # The fragrament shader uses rasterized texture coordinates `v_texcoord`
        # connect texture and the shader, so that we can render pixels with texture values
        cube_texture = GpuTexture(cpu_image=Image.open('texture.jpeg'))
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, cube_texture.gpu_id)

        glUseProgram(self.shader_program)
        uniTex = glGetUniformLocation(self.shader_program, "tex")
        glUniform1i(uniTex, 0)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(1,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader_program)
        glBindVertexArray(self.vao)
        glLineWidth(10)
        # glDrawElements(GL_LINES, 6, GL_UNSIGNED_INT, 0)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0)


    def unload(self):
        super().unload()
        if not self.is_loaded:
            return
        self.is_loaded = False

        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(2, [self.vbo, self.ebo])
        glDeleteProgram(self.shader_program)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)
        del self.vao, self.vbo, self.ebo
        del self.shader_program, self.vertex_shader, self.fragment_shader
        # TODO: delete texture

    def get_shader_log(self, shader):
        '''Return the shader log'''
        return self.get_log(shader, glGetShaderInfoLog)

    def get_program_log(self, shader):
        '''Return the program log'''
        return self.get_log(shader, glGetProgramInfoLog)

    def get_log(self, obj, func):
        value = func(obj)
        return value





