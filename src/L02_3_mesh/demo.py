from dataclasses import dataclass
import math
from ..common.gl_texture import GpuTexture
from ..common.gl_shader import GpuShader
from ..demos_loader import Demo
from OpenGL.GL import *
from PIL import Image
import numpy as np
import glfw
import pyrr
import pywavefront

@dataclass
class UiDefaults:
    color: int

class Lecture02_MeshDemo(Demo):
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
        cpu_image = Image.open('../../assets/human_head/lambertian.jpg').transpose(Image.FLIP_TOP_BOTTOM)
        self.texture = GpuTexture(cpu_image)
        # self.texture = GpuTexture(cpu_image=Image.open('../../assets/spot_cow/spot_texture.png'))

        self.shader.use()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture.gpu_id)
        uniform_texture = glGetUniformLocation(self.shader.shader_program, "u_texture")
        glUniform1i(uniform_texture, 0)


    def make_vertex_data(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        scene = pywavefront.Wavefront('../../assets/human_head/head.obj', collect_faces=True)
        # scene = pywavefront.Wavefront('../../assets/spot_cow/spot_control_mesh.obj', collect_faces=True)
        material = scene.materials['defaultMat']

        mesh_data = material.vertices
        mesh_data = np.asarray(mesh_data, dtype=np.float32).reshape(-1, 5)
        float_nbytes = mesh_data.itemsize

        positions = np.ascontiguousarray(mesh_data[:, 2:], dtype=np.float32)
        uvs = np.ascontiguousarray(mesh_data[:, :2])
        self.n_vertices = len(mesh_data)

        # send data to GPU
        self.gpu_positions, self.gpu_texture_coords = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_positions)
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        shader_id = self.shader.use()
        position_attribute = glGetAttribLocation(shader_id, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            3,
            GL_FLOAT,
            GL_FALSE,
            3*float_nbytes,
            None,
        )

        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_texture_coords)
        glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)

        texture_coords_attribute = glGetAttribLocation(shader_id, "a_texture_coords")
        glEnableVertexAttribArray(texture_coords_attribute)
        glVertexAttribPointer(texture_coords_attribute,
            2,
            GL_FLOAT,
            GL_FALSE,
            2*float_nbytes,
            None)

        # make an index buffer
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)

        faces = scene.meshes[None].faces
        self.faces = np.ascontiguousarray(faces, dtype=np.uint32).flatten()

        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0.0,0.0,0.0,1)
        # glClear(GL_COLOR_BUFFER_BIT)

        # CLEAR Z-BUFFER
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        glUniform1f(uniform_aspect, width / height)

        # make rotation, scale, translation
        #time_sin = np.sin(global_time_sec)
        #time_cos = np.cos(global_time_sec)

        scale_all = 2.0 #4.472662
        scale = pyrr.Matrix44.from_scale((scale_all, scale_all, scale_all), dtype=np.float32)
        rotation = pyrr.Matrix44.from_eulers((0.0, 0.0, global_time_sec), dtype=np.float32)
        translation = pyrr.Matrix44.from_translation((0.0, 0.1, 0.0), dtype=np.float32)

        transform = translation @ rotation @ scale
        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, transform)

        glBindVertexArray(self.vao)
        # glDrawElements(GL_TRIANGLES, len(self.faces), GL_UNSIGNED_INT, None)
        print(self.n_vertices)
        glDrawArrays(GL_TRIANGLES, 0, self.n_vertices)


    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDisable(GL_DEPTH_TEST)
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(2, np.asarray([self.gpu_positions, self.gpu_texture_coords], dtype=np.uint32))
        del self.shader
        del self.vao, self.gpu_positions, self.gpu_texture_coords
        del self.texture
        super().unload()





