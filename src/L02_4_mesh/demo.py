from ..common.texture_drawer import TextureDrawer
from ..common.gl_texture import GpuTexture
from ..common.gl_shader import GpuShader
from ..common.obj_loader import ParsedWavefront
from ..demos_loader import Demo
from ..common.defines import *
from OpenGL.GL import *
from typing import Optional
from PIL import Image
import numpy as np
import glfw
import pyrr

class GpuMesh:
    def __init__(self, obj_filepath: str, texture_filepath: str = None, texture_unit: int = None, use_index_buffer=True):
        self.position_n_coords = 3
        self.texcoord_n_coords = 2
        self.position_location, self.texcoord_location = None, None
        self.obj_filepath = obj_filepath
        self.texture_filepath = texture_filepath
        self.texture_unit = texture_unit
        self.use_index_buffer = use_index_buffer

    def with_attributes_size(self, position_n_coords: int, texcoord_n_coords: int):
        self.position_n_coords = position_n_coords
        self.texcoord_n_coords = texcoord_n_coords
        return self

    def with_attributes_shader_location(self, position_location: int, texcoord_location: int):
        self.position_location = position_location
        self.texcoord_location = texcoord_location
        return self

    def build(self, verbose=True):
        assert self.position_location is not None and self.texcoord_location is not None
        self.load_vertex_data(self.obj_filepath, verbose=verbose)
        self.load_texture(self.texture_filepath)
        self.is_built = True
        return self

    @property
    def has_index_buffer(self):
        return self.use_index_buffer

    @property
    def n_draw_elements(self):
        return self.n_elements

    def use(self):
        assert self.is_built
        glBindVertexArray(self.vao)
        if self.texture is not None:
            glActiveTexture(GL_TEXTURE0 + self.texture_unit)
            glBindTexture(GL_TEXTURE_2D, self.texture.gpu_id)
        return self.vao

    def load_vertex_data(self, obj_filepath: str, verbose=True):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        scene = ParsedWavefront(obj_filepath, verbose=verbose)

        attributes_layout = f'P{self.position_n_coords}_T{self.texcoord_n_coords}'
        if self.use_index_buffer:
            attributes, index_array = scene.as_numpy_indexed(attributes_layout)
            self.n_elements = len(index_array)
        else:
            attributes = scene.as_numpy(attributes_layout)
            self.n_elements = attributes.shape[0]

        # send data to GPU
        self.gpu_attributes = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.gpu_attributes)
        glBufferData(GL_ARRAY_BUFFER, attributes.nbytes, attributes, GL_STATIC_DRAW)
        if self.use_index_buffer:
            self.gpu_index_array = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.gpu_index_array)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_array.nbytes, index_array, GL_STATIC_DRAW)

        # connect a shader variable and vertex data
        float_nbytes = attributes.itemsize
        attributes_stride = (self.position_n_coords + self.texcoord_n_coords) * float_nbytes

        glEnableVertexAttribArray(self.position_location)
        glVertexAttribPointer(self.position_location,
            self.position_n_coords,
            GL_FLOAT,
            GL_FALSE,
            attributes_stride,
            ctypes.c_void_p(0),
        )

        glEnableVertexAttribArray(self.texcoord_location)
        glVertexAttribPointer(self.texcoord_location,
            self.texcoord_n_coords,
            GL_FLOAT,
            GL_FALSE,
            attributes_stride,
            ctypes.c_void_p(self.position_n_coords*float_nbytes))

        # unbind for safety
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def load_texture(self, texture_filepath):
        if texture_filepath is not None:
            cpu_image = Image.open(texture_filepath).transpose(Image.FLIP_TOP_BOTTOM)
            self.texture = GpuTexture(cpu_image)
        else:
            self.texture = None

    def __del__(self):
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        if self.use_index_buffer:
            glDeleteBuffers(2, np.asarray([self.gpu_attributes, self.gpu_index_array], dtype=np.uint32))
        else:
            glDeleteBuffers(1, np.asarray([self.gpu_attributes], dtype=np.uint32))
        del self.texture

class Lecture02_MeshDemo(Demo):
    def __init__(self):
        super().__init__(ui_defaults=None)
        self.meshes = []

    def load(self, window):
        super().load(window)

        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')

        shader_id = self.shader.use()
        position_shader_location = glGetAttribLocation(shader_id, "a_position")
        texcoord_shader_location = glGetAttribLocation(shader_id, "a_texture_coords")
        if len(self.meshes) == 0:
            position_n_coords, texcoord_n_coords = 3, 2
            head_mesh = GpuMesh(
                obj_filepath='../../assets/human_head/head.obj',
                texture_filepath='../../assets/human_head/lambertian.jpg',
                texture_unit=0, # bound once to GL_TEXTURE0, used later for all the frames
                use_index_buffer=True)
            head_mesh.with_attributes_size(position_n_coords, texcoord_n_coords)
            head_mesh.with_attributes_shader_location(position_shader_location, texcoord_shader_location)
            self.meshes.append(head_mesh.build(verbose=False))
            print('Loaded head mesh and texture, n_elements:', self.meshes[-1].n_draw_elements)

            cow_mesh = GpuMesh(
                obj_filepath='../../assets/spot_cow/spot_triangulated.obj',
                texture_filepath='../../assets/spot_cow/spot_texture.png',
                texture_unit=1, # bound once to GL_TEXTURE0, used later for all the frames
                use_index_buffer=True)
            cow_mesh.with_attributes_size(position_n_coords, texcoord_n_coords)
            cow_mesh.with_attributes_shader_location(position_shader_location, texcoord_shader_location)
            self.meshes.append(cow_mesh.build())
            print('Loaded cow mesh and texture, n_elements:', self.meshes[-1].n_draw_elements)

        # Draw textures used in this demo, totally unnecessary and for visualization purposes
        self.draw_textures = False

        self.head_texture_drawer = TextureDrawer((-1,-0.25), (-0.5,0.25))
        head_texture_id = self.meshes[0].texture.gl_id
        head_texture_unit = self.meshes[0].texture_unit # 0
        self.head_texture_drawer.attach_texture(head_texture_id, head_texture_unit)

        cow_texture_id = self.meshes[1].texture.gl_id
        cow_texture_unit = self.meshes[1].texture_unit # 0
        self.cow_texture_drawer = TextureDrawer((0.5,-0.25), (1,0.25))
        self.cow_texture_drawer.attach_texture(cow_texture_id, cow_texture_unit)

        # enable Z-buffer
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        self.is_loaded = True

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0.0,0.0,0.0,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        aspect_ratio = width / height
        glUniform1f(uniform_aspect, aspect_ratio)

        shader_id = self.shader.use()
        uniform_texture = glGetUniformLocation(shader_id, "u_texture")
        for i, mesh in enumerate(self.meshes):
            # set the appropriate texture for the shader
            glUniform1i(uniform_texture, i) # we bound head texture to unit 0 and cow's to unit 1

            # make rotation, scale, translation
            if i == 0:
                scale = 2.0
                translation = (0.0, 0.1, 0.3)
            else:
                scale = 0.5
                translation = (0.0, 0.0, -1.0)

            scale = pyrr.Matrix44.from_scale((scale, scale, scale), dtype=np.float32)

            rotation = pyrr.Matrix44.from_eulers((0.0, 0.0, global_time_sec/2), dtype=np.float32)

            translation = pyrr.Matrix44.from_translation(translation, dtype=np.float32)

            transform = translation @ rotation @ scale

            uniform_transform = glGetUniformLocation(shader_id, "u_transform")
            glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, transform)

            mesh.use()
            if mesh.has_index_buffer:
                glDrawElements(GL_TRIANGLES, mesh.n_draw_elements, GL_UNSIGNED_INT, None)
            else:
                glDrawArrays(GL_TRIANGLES, 0, mesh.n_draw_elements)

        # just for visualization
        if self.draw_textures:
            self.head_texture_drawer.render(aspect_ratio)
            self.cow_texture_drawer.render(aspect_ratio)


    def keyboard_callback(self, window, key, scancode, action, mods):
        super().keyboard_callback(window, key, scancode, action, mods)
        if (key, action) == (glfw.KEY_Q, glfw.PRESS):
            self.draw_textures = not self.draw_textures

    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDisable(GL_DEPTH_TEST)
        # for mesh in self.meshes:
        #     del mesh
        del self.shader
        super().unload()





