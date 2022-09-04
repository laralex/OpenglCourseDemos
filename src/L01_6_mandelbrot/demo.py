from dataclasses import dataclass
import math
from ..common.gl_texture import GpuTexture
from ..common.gl_shader import GpuShader
from ..all_demos import Demo
from OpenGL.GL import *
from PIL import Image
import numpy as np

@dataclass
class UiDefaults:
    color: int

class Lecture01_MandelbrotDemo(Demo):
    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def load(self, window):
        super().load(window)

        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')
        self.texture = GpuTexture(cpu_image=Image.open('../textures/pallete_1d.png'), is_1d=True)

        self.shader.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_1D, self.texture.gpu_id)
        uniform_texture = glGetUniformLocation(self.shader.shader_program, "u_palette")
        glUniform1i(uniform_texture, 0)

        uniform_center = glGetUniformLocation(self.shader.shader_program, "u_center")
        #glUniform2d(uniform_center, 0.77568377, -0.13646737)
        glUniform2f(uniform_center, 0.10109636384562, -0.95628651080914)

        self.make_vertex_data()

        self.zoom = 10.0
        self.is_loaded = True

    def make_vertex_data(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        positions = np.array((
            # X     Y
            -1.0, -1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ), dtype=np.float32, order='C')

        float_nbytes = positions.itemsize # 4

        screen_coords = np.array((
            # U    V
            -1.0, -1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ), dtype=np.float32, order='C')

        # send data to GPU
        self.gpu_positions, self.gpu_screen_coords = glGenBuffers(2)
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
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_screen_coords)
        glBufferData(GL_ARRAY_BUFFER, screen_coords.nbytes, screen_coords, GL_STATIC_DRAW)

        screen_coords_attribute = glGetAttribLocation(shader_id, "a_screen_coords")
        glEnableVertexAttribArray(screen_coords_attribute)
        glVertexAttribPointer(screen_coords_attribute,
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

        uniform_aspect = glGetUniformLocation(shader_id, "u_zoom")
        self.zoom /= 1.0118
        glUniform1f(uniform_aspect, self.zoom)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)


    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(2, np.asarray([self.gpu_positions, self.gpu_screen_coords], dtype=np.uint32))
        del self.shader
        del self.vao, self.gpu_positions, self.gpu_screen_coords
        super().unload()





