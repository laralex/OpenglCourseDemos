from ..common.gl_shader import GpuShader
from ..common.defines import *
from OpenGL.GL import *
from typing import Tuple
import numpy as np
import pyrr

class TextureDrawer:
    """
    Allows to visualize texture content on the screen
    """
    Coords = Tuple[float, float]
    def __init__(self, left_bottom_ncd: Coords, right_top_ndc: Coords):
        self.left_ndc, self.bottom_ndc = left_bottom_ncd
        self.right_ndc, self.top_ndc = right_top_ndc
        self.width_ndc = self.right_ndc - self.left_ndc
        self.height_ndc = self.top_ndc - self.bottom_ndc

        self.gl_texture = None
        self.gl_texture_unit = None

        translation = pyrr.Matrix44.from_translation([
            (self.left_ndc + self.right_ndc)*0.5,
            -(self.bottom_ndc + self.top_ndc)*0.5,
            0], dtype=np.float32)
        scale = pyrr.Matrix44.from_scale([self.width_ndc, -self.height_ndc, 1.0], dtype=np.float32)
        self.transform = scale @ translation
        self.shader = GpuShader(
            '../common/shaders/transform_vert.glsl',
            '../common/shaders/texture_frag.glsl',
            out_variable=b'out_color')

        self.make_vertex_attributes()

    def attach_texture(self, texture_opengl_id, texture_opengl_unit):
        glActiveTexture(GL_TEXTURE0 + texture_opengl_unit)
        glBindTexture(GL_TEXTURE_2D, texture_opengl_id)
        shader_id = self.shader.use()
        uniform_texture = glGetUniformLocation(shader_id, "u_texture")
        glUniform1i(uniform_texture, texture_opengl_unit)
        self.gl_texture = texture_opengl_id
        self.gl_texture_unit = texture_opengl_unit

    def make_vertex_attributes(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # interleaved attributes
        attributes = np.array((
            # X     Y    Z    U    V
            -0.5, -0.5, -0.99, 0.0, 1.0,
            -0.5,  0.5, -0.99, 0.0, 0.0,
             0.5, -0.5, -0.99, 1.0, 1.0,
             0.5,  0.5, -0.99, 1.0, 0.0,
        ), dtype=np.float32, order='C')

        float_nbytes = attributes.itemsize

        # send data to GPU
        self.gl_attributes = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.gl_attributes)
        glBufferData(GL_ARRAY_BUFFER, attributes.nbytes, attributes, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        shader_id = self.shader.use()
        stride = 5*float_nbytes

        position_attribute = glGetAttribLocation(shader_id, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            None
        )

        # same for texture coordinates
        texture_coords_attribute = glGetAttribLocation(shader_id, "a_custom_data")
        glEnableVertexAttribArray(texture_coords_attribute)
        glVertexAttribPointer(texture_coords_attribute,
            2,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(3*float_nbytes))

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def render(self, aspect_ratio):
        assert self.gl_texture is not None

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        glUniform1f(uniform_aspect, aspect_ratio)

        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, self.transform)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    def __del__(self):
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(1, np.asarray([self.gl_attributes], dtype=np.uint32))
        del self.shader
        del self.vao, self.gl_attributes
