from dataclasses import dataclass
import math
from tabnanny import verbose
from ..common.gl_texture import GpuTexture
from ..common.gl_shader import GpuShader
from ..common.obj_loader import ParsedWavefront
from ..demos_loader import Demo
from OpenGL.GL import *
from PIL import Image
import numpy as np
import glfw
import pyrr

class GpuMesh:
    def __init__(self, obj_filepath, texture_filepath, position_n_coords, uv_n_coords, shader):
        self.load_vertex_data(obj_filepath, position_n_coords, uv_n_coords, shader)
        self.load_texture(texture_filepath)

    def use(self):
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture.gpu_id)
        return self.vao

    def load_vertex_data(self, obj_filepath: str, position_n_coords: int, uv_n_coords: int, shader):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        scene = ParsedWavefront(obj_filepath, verbose=True)

        attibutes, index_array = scene.as_numpy_indexed(f'P{position_n_coords}_T{uv_n_coords}')

        self.n_elements = len(index_array)

        # send data to GPU
        self.gpu_attributes, self.gpu_index_array = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_attributes)
        glBufferData(GL_ARRAY_BUFFER, attibutes.nbytes, attibutes, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.gpu_index_array)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_array.nbytes, index_array, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        float_nbytes = 4
        attributes_stride = (position_n_coords + uv_n_coords) * float_nbytes

        shader_id = shader.use()
        position_attribute = glGetAttribLocation(shader_id, "a_position")
        glEnableVertexAttribArray(position_attribute)
        glVertexAttribPointer(position_attribute,
            position_n_coords,
            GL_FLOAT,
            GL_FALSE,
            attributes_stride,
            ctypes.c_void_p(0),
        )

        texture_coords_attribute = glGetAttribLocation(shader_id, "a_texture_coords")
        glEnableVertexAttribArray(texture_coords_attribute)
        glVertexAttribPointer(texture_coords_attribute,
            uv_n_coords,
            GL_FLOAT,
            GL_FALSE,
            attributes_stride,
            ctypes.c_void_p(position_n_coords*float_nbytes))

        # unbind for safety
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def load_texture(self, texture_filepath):
        cpu_image = Image.open(texture_filepath).transpose(Image.FLIP_TOP_BOTTOM)
        self.texture = GpuTexture(cpu_image)

    def __del__(self):
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(2, np.asarray([self.gpu_attributes, self.gpu_index_array], dtype=np.uint32))
        del self.texture

class Lecture02_MeshDemo(Demo):
    def __init__(self):
        super().__init__(ui_defaults=None)
        self.meshes = []

    def load(self, window):
        super().load(window)

        self.position_n_coords, self.uv_n_coords = 3, 2
        self.make_shader()

        if len(self.meshes) == 0:
            self.meshes.append(GpuMesh(
                obj_filepath='../../assets/human_head/head.obj',
                texture_filepath='../../assets/human_head/lambertian.jpg',
                position_n_coords=self.position_n_coords,
                uv_n_coords=self.uv_n_coords,
                shader=self.shader,
            ))
            print('Loaded head mesh and texture, n_elements:', self.meshes[-1].n_elements)
            self.meshes.append(GpuMesh(
                obj_filepath='../../assets/spot_cow/spot_triangulated.obj',
                texture_filepath='../../assets/spot_cow/spot_texture.png',
                position_n_coords=self.position_n_coords,
                uv_n_coords=self.uv_n_coords,
                shader=self.shader,
            ))
            print('Loaded cow mesh and texture, n_elements:', self.meshes[-1].n_elements)
            self.current_mesh = 0


        # enable Z-buffer
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        self.is_loaded = True

    def make_shader(self):
        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')
        self.shader.use()
        uniform_texture = glGetUniformLocation(self.shader.shader_program, "u_texture")
        glUniform1i(uniform_texture, 0)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0.0,0.0,0.0,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        glUniform1f(uniform_aspect, width / height)

        # make rotation, scale, translation
        scale_all = 2.0 if self.current_mesh == 0 else 0.5
        scale = pyrr.Matrix44.from_scale((scale_all, scale_all, scale_all), dtype=np.float32)
        rotation = pyrr.Matrix44.from_eulers((0.0, 0.0, global_time_sec), dtype=np.float32)
        translation = pyrr.Matrix44.from_translation((0.0, 0.1, 0.0), dtype=np.float32)

        transform = translation @ rotation @ scale
        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, transform)

        mesh = self.meshes[self.current_mesh]
        mesh.use()
        self.shader.use()
        glDrawElements(GL_TRIANGLES, mesh.n_elements, GL_UNSIGNED_INT, None)
        # glDrawArrays(GL_TRIANGLES, 0, self.n_vertices)

    def keyboard_callback(self, window, key, scancode, action, mods):
        if (key, action) == (glfw.KEY_R, glfw.PRESS):
            self.current_mesh = (self.current_mesh + 1) % len(self.meshes)
            print('Current mesh', 'head' if self.current_mesh == 0 else 'cow')
        super().keyboard_callback(window, key, scancode, action, mods)

    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDisable(GL_DEPTH_TEST)
        # for mesh in self.meshes:
        #     del mesh
        del self.shader
        super().unload()





