from dataclasses import dataclass
from ..common.gpu_texture import GpuTexture
from ..common.gpu_shader import GpuShader
from ..demos_loader import Demo
from ..common.defines import *
from OpenGL.GL import *
from PIL import Image
import numpy as np
import pyrr

@dataclass
class UiDefaults:
    color: int

class Lecture02_CubeInterleavedDemo(Demo):
    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def load(self, window):
        super().load(window)
        self.make_shader()
        self.make_vertex_data()

        # ENABLE Z-BUFFER
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        self.is_loaded = True

    def make_shader(self):
        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')
        self.texture = GpuTexture(cpu_image=Image.open('../../assets/crate_color.jpeg'))
        self.texture.use(texture_unit=0)
        self.shader.use()
        uniform_texture = glGetUniformLocation(self.shader.shader_program, "u_texture")
        glUniform1i(uniform_texture, 0)


    def make_vertex_data(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # positions, then texture coords
        attributes = np.array((
            # X    Y    Z    U    V
            -1.0,-1.0,-1.0, 0.0, 0.0, # 0
            -1.0,-1.0, 1.0, 1.0, 0.0, # 1
            -1.0, 1.0, 1.0, 1.0, 1.0, # 2
            -1.0, 1.0,-1.0, 0.0, 1.0, # 3
             1.0,-1.0,-1.0, 1.0, 0.0, # 4
             1.0,-1.0, 1.0, 0.0, 0.0, # 5
             1.0, 1.0, 1.0, 0.0, 1.0, # 6
             1.0, 1.0,-1.0, 1.0, 1.0, # 7
            -1.0, 1.0, 1.0, 0.0, 0.0, # 8
            -1.0, 1.0,-1.0, 1.0, 0.0, # 9
             1.0,-1.0,-1.0, 0.0, 1.0, # 10
             1.0,-1.0, 1.0, 1.0, 1.0, # 11
        ), dtype=np.float32, order='C')

        float_nbytes = attributes.itemsize # 4

        # send data to GPU
        self.gpu_attributes = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_attributes)
        glBufferData(GL_ARRAY_BUFFER, attributes.nbytes, attributes, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        shader_id = self.shader.use()
        position_attribute = glGetAttribLocation(shader_id, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            3,
            GL_FLOAT,
            GL_FALSE,
            5*float_nbytes, # stride 3 + 2 !!
            ctypes.c_void_p(0*float_nbytes), # offset 0 !!
        )

        texture_coords_attribute = glGetAttribLocation(shader_id, "a_texture_coords")
        glEnableVertexAttribArray(texture_coords_attribute)
        glVertexAttribPointer(texture_coords_attribute,
            2,
            GL_FLOAT,
            GL_FALSE,
            5*float_nbytes, # stride 3 + 2 !!
            ctypes.c_void_p(3*float_nbytes), # offset 3 !!
        )

        # make an index buffer
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        triangle_indices = np.array((
          # v1  v2  v3
            1,  5,  2,
            2,  5,  6,
            3,  7,  0,
            0,  7,  4,
            1,  2,  0,
            0,  2,  3,
            6,  5,  7,
            7,  5,  4,

            # old 12 positions -> wrong coordinates
            # 0,  4,  1,
            # 1,  4,  5,
            # 2,  6,  3,
            # 3,  6,  7,

            # duplicated positions, 16 total -> correct
            0, 10,  1,
            1, 10, 11,
            8,  6,  9,
            9,  6,  7,
        ), dtype=np.uint32)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, triangle_indices.nbytes, triangle_indices, GL_STATIC_DRAW)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0,0,0,1)

        # CLEAR Z-BUFFER
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        glUniform1f(uniform_aspect, width / height)

        # make rotation, scale, translation
        time_sin = np.sin(global_time_sec)
        time_cos = np.cos(global_time_sec)

        scale_all = 0.2
        scale = pyrr.Matrix44.from_scale((scale_all, scale_all, scale_all), dtype=np.float32)
        rotation = pyrr.Matrix44.from_eulers((time_sin, time_cos, time_sin), dtype=np.float32)
        translation = pyrr.Matrix44.from_translation((0.0, 0.0, 0.0), dtype=np.float32)

        transform = translation @ rotation @ scale
        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, transform)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 12*3, GL_UNSIGNED_INT, None)


    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDisable(GL_DEPTH_TEST)
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(1, np.asarray([self.gpu_attributes], dtype=np.uint32))
        del self.shader
        del self.vao, self.gpu_attributes
        del self.texture
        super().unload()





