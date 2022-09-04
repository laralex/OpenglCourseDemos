from dataclasses import dataclass
import math
from ..common.gl_texture import GpuTexture
from ..common.gl_shader import GpuShader
from ..all_demos import Demo
from OpenGL.GL import *
from PIL import Image
import numpy as np
import glfw
import pyrr

@dataclass
class UiDefaults:
    color: int

class Lecture01_TransformMatrixDemo(Demo):
    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def load(self, window):
        super().load(window)
        self.make_shader()
        self.make_vertex_data()
        self.is_loaded = True
        self.draw_mode = GL_TRIANGLE_STRIP

    def make_shader(self):
        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')

        # The fragrament shader uses rasterized texture coordinates `v_texcoord`
        # connect texture and the shader, so that we can render pixels with texture values
        self.texture = GpuTexture(cpu_image=Image.open('../textures/crate_color.jpeg'))

        self.shader.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture.gpu_id)
        uniform_texture = glGetUniformLocation(self.shader.shader_program, "u_texture")
        glUniform1i(uniform_texture, 0)


    def make_vertex_data(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        positions = np.array((
            # X     Y
            -0.5, -0.5,
            -0.5,  0.5,
             0.5, -0.5,
             0.5,  0.5,
        ), dtype=np.float32, order='C')

        float_nbytes = positions.itemsize # 4

        texture_coords = np.array((
            # U    V
             0.0, 1.0,
             0.0, 0.0,
             1.0, 1.0,
             1.0, 0.0,
        ), dtype=np.float32, order='C')

        # send data to GPU
        self.gpu_positions, self.gpu_texture_coords = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_positions)
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        shader_id = self.shader.use()
        position_attribute = glGetAttribLocation(shader_id, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            2,
            GL_FLOAT,
            GL_FALSE,
            2*float_nbytes,
            None
        )

        # same for texture coordinates
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_texture_coords)
        glBufferData(GL_ARRAY_BUFFER, texture_coords.nbytes, texture_coords, GL_STATIC_DRAW)

        texture_coords_attribute = glGetAttribLocation(shader_id, "a_texture_coords")
        glEnableVertexAttribArray(texture_coords_attribute)
        glVertexAttribPointer(texture_coords_attribute,
            2,
            GL_FLOAT,
            GL_FALSE,
            2*float_nbytes,
            None)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        glUniform1f(uniform_aspect, width / height)

        # === CHANGE #3
        # make rotation, scale, translation
        time_sin = np.sin(global_time_sec)
        time_cos = np.cos(global_time_sec)

        scale_x = scale_y = (time_cos + 1.1) * 0.5
        # scale = np.eye(3, dtype=np.float32)
        scale = np.array([
            [scale_x ,     0.0, 0.0],
            [0.0     , scale_y, 0.0],
            [0.0     ,     0.0, 1.0],
        ], dtype=np.float32)

        # rotation = np.eye(3, dtype=np.float32)
        translation_x, translation_y = 0.0, time_sin * 0.5
        rotation_translation = np.array([
            [time_sin     ,      time_cos, 0.0],
            [time_cos     ,     -time_sin, 0.0],
            [translation_x, translation_y, 1.0],
        ], dtype=np.float32)

        transform = rotation_translation @ scale
        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix3fv(uniform_transform, 1, GL_FALSE, transform)

        glBindVertexArray(self.vao)
        glDrawArrays(self.draw_mode, 0, 4)


    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(2, np.asarray([self.gpu_positions, self.gpu_texture_coords], dtype=np.uint32))
        del self.shader
        del self.vao, self.gpu_positions, self.gpu_texture_coords
        del self.texture
        super().unload()

    def keyboard_callback(self, window, key, scancode, action, mods):
        if (key, action) == (glfw.KEY_T, glfw.PRESS):
            if self.draw_mode == GL_TRIANGLE_STRIP:
                self.draw_mode = GL_LINE_STRIP
            else:
                self.draw_mode = GL_TRIANGLE_STRIP
        return super().keyboard_callback(window, key, scancode, action, mods)





