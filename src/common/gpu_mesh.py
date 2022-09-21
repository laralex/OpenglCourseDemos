from .gpu_texture import GpuTexture
from ..common.obj_loader import ParsedWavefront
from ..base_demo import BaseDemo
from ..common.defines import *
from OpenGL.GL import *
from PIL import Image
import numpy as np

class GpuMesh:
    def __init__(self, obj_filepath: str, use_index_buffer=True):
        self.position_n_coords = None
        self.texcoord_n_coords = None
        self.normals_n_coords  = None
        self.position_location = None
        self.texcoord_location = None
        self.normals_location  = None
        self.obj_filepath = obj_filepath
        self.use_index_buffer = use_index_buffer
        self.is_built = False

    def with_attributes_size(self, position_n_coords: int, texcoord_n_coords: int, normals_n_coords: int):
        self.position_n_coords = position_n_coords
        self.texcoord_n_coords = texcoord_n_coords
        self.normals_n_coords  = normals_n_coords
        return self

    def with_attributes_shader_location(self, position_location: int, texcoord_location: int, normals_location: int):
        self.position_location = position_location
        self.texcoord_location = texcoord_location
        self.normals_location = normals_location
        return self

    def build(self, verbose=True):
        assert self.position_location is not None and self.position_n_coords > 0
        assert (self.texcoord_location is None) == (self.texcoord_n_coords == 0)
        assert (self.normals_location is None) == (self.normals_n_coords == 0)
        self.load_vertex_data(self.obj_filepath, verbose=verbose)
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
        return self.vao

    def make_wavefront_layout_pattern(self):
        pos = f'P{self.position_n_coords}' if self.position_n_coords else ''
        tex = f'T{self.texcoord_n_coords}' if self.texcoord_n_coords else ''
        normals = f'N{self.normals_n_coords}' if self.normals_n_coords else ''
        return '_'.join( filter(bool, [pos, tex, normals]) )

    def load_vertex_data(self, obj_filepath: str, verbose=True):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        scene = ParsedWavefront(obj_filepath, verbose=verbose)

        attributes_layout = self.make_wavefront_layout_pattern()
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
        attributes_stride = (self.position_n_coords + self.texcoord_n_coords + self.normals_n_coords) * float_nbytes

        if self.position_location is not None:
            glEnableVertexAttribArray(self.position_location)
            glVertexAttribPointer(self.position_location,
                self.position_n_coords,
                GL_FLOAT,
                GL_FALSE,
                attributes_stride,
                ctypes.c_void_p(0),
            )

        if self.texcoord_location is not None:
            glEnableVertexAttribArray(self.texcoord_location)
            glVertexAttribPointer(self.texcoord_location,
                self.texcoord_n_coords,
                GL_FLOAT,
                GL_FALSE,
                attributes_stride,
                ctypes.c_void_p(self.position_n_coords*float_nbytes))

        if self.normals_location is not None:
            glEnableVertexAttribArray(self.normals_location)
            glVertexAttribPointer(self.normals_location,
                self.normals_n_coords,
                GL_FLOAT,
                GL_FALSE,
                attributes_stride,
                ctypes.c_void_p((self.position_n_coords+self.texcoord_n_coords)*float_nbytes))

        # unbind for safety
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def __del__(self):
        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        if self.use_index_buffer:
            glDeleteBuffers(2, np.asarray([self.gpu_attributes, self.gpu_index_array], dtype=np.uint32))
        else:
            glDeleteBuffers(1, np.asarray([self.gpu_attributes], dtype=np.uint32))