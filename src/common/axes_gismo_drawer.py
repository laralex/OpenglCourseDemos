from ..common.gl_shader import GpuShader
from ..common.defines import *
from OpenGL.GL import *
from typing import Tuple
import numpy as np
import pyrr

class AxesGismoDrawer:
    """
    Allows to visualize texture content on the screen
    """
    Coords = Tuple[float, float]
    def __init__(self):
        self.shader = GpuShader(
            '../common/shaders/transform_vert.glsl',
            '../common/shaders/color_frag.glsl',
            out_variable=b'out_color')

        self.make_vertex_attributes()

    def make_vertex_attributes(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # interleaved attributes
        attributes = np.array((
            # X     Y    Z     R     G     B
            0.0,  0.0,  0.0,  1.0,  0.0,  0.0,  #0
            1.0,  0.0,  0.0,  1.0,  0.0,  0.0,  #1
            0.9,  0.1,  0.0,  1.0,  0.0,  0.0,  #2
            0.9, -0.1,  0.0,  1.0,  0.0,  0.0,  #3
            0.9,  0.0,  0.1,  1.0,  0.0,  0.0,  #4
            0.9,  0.0, -0.1,  1.0,  0.0,  0.0,  #5
            0.0,  0.0,  0.0,  0.0,  1.0,  0.0,  #6
            0.0,  1.0,  0.0,  0.0,  1.0,  0.0,  #7
            0.1,  0.9,  0.0,  0.0,  1.0,  0.0,  #8
           -0.1,  0.9,  0.0,  0.0,  1.0,  0.0,  #9
            0.0,  0.9,  0.1,  0.0,  1.0,  0.0,  #10
            0.0,  0.9, -0.1,  0.0,  1.0,  0.0,  #11
            0.0,  0.0,  0.0,  0.0,  0.0,  1.0,  #12
            0.0,  0.0,  1.0,  0.0,  0.0,  1.0,  #13
            0.1,  0.0,  0.9,  0.0,  0.0,  1.0,  #14
           -0.1,  0.0,  0.9,  0.0,  0.0,  1.0,  #15
            0.0,  0.1,  0.9,  0.0,  0.0,  1.0,  #16
            0.0, -0.1,  0.9,  0.0,  0.0,  1.0,  #17
        ), dtype=np.float32, order='C')

        SCALE = 0.5
        for i in range(3):
            attributes[i::6] *= SCALE

        float_nbytes = attributes.itemsize

        # send data to GPU
        self.gl_attributes = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.gl_attributes)
        glBufferData(GL_ARRAY_BUFFER, attributes.nbytes, attributes, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        shader_id = self.shader.use()
        stride = 6*float_nbytes

        position_attribute = glGetAttribLocation(shader_id, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            None
        )

        color_attribute = glGetAttribLocation(shader_id, "a_custom_data")
        glEnableVertexAttribArray(color_attribute)
        glVertexAttribPointer(color_attribute,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(3*float_nbytes))

        self.gl_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.gl_index_buffer)
        lines_indices = np.array((
            0, 1,
            1, 2,
            # 1, 3,
            1, 4,
            # 1, 5,
            6, 7,
            7, 8,
            # 7, 9,
            7, 10,
            # 7, 11,
            12, 13,
            13, 14,
            # 13, 15,
            13, 16,
            # 13, 17,
        ), dtype=np.uint32)
        self.n_elements = lines_indices.size
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, lines_indices.nbytes, lines_indices, GL_STATIC_DRAW)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def set_transform(self, transform):
        assert isinstance(transform, np.ndarray) and transform.size == 16
        self.transform = transform
        self.shader.use()
        uniform_transform = glGetUniformLocation(self.shader.shader_program, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, self.transform)

    def render(self, aspect_ratio):
        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        glUniform1f(uniform_aspect, aspect_ratio)
        glBindVertexArray(self.vao)
        glDrawElements(GL_LINES, self.n_elements, GL_UNSIGNED_INT, None)

    def __del__(self):
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(2, np.asarray([self.gl_attributes, self.gl_index_buffer], dtype=np.uint32))
        del self.shader
        del self.vao, self.gl_attributes, self.gl_index_buffer