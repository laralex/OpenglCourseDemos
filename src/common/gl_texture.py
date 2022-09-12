from . import defines
from OpenGL.GL import *
from PIL.Image import Image
import numpy as np



class GpuTexture:
    # All next configuring commands will affect this newly created texture object
    def bind(self):
        glBindTexture(self.target, self.gpu_id)

    @property
    def gl_id(self):
        return self.gpu_id

    @property
    def gl_target(self):
        return self.target

    @property
    def size_pixels(self):
        return (self.width, self.height)

    def __init__(self, cpu_image: Image, is_1d=False):
        assert isinstance(cpu_image, Image)
        self.width, self.height = cpu_image.size
        if is_1d:
            self.target = GL_TEXTURE_1D
        else:
            self.target = GL_TEXTURE_2D


        if cpu_image.mode == 'RGB':
            cpu_format = GL_RGB
        elif cpu_image.mode == 'RGBA':
            cpu_format = GL_RGBA
        else:
            raise NotImplementedError('Not currently supporting other fancy image formats')

        # OpenGL creates a unique texture identifier (just a number) on its GPU side
        # and returns it to our CPU-side code, it's a cheap way for us 
        # to communicate to GPU which texture among all we want to use
        # ! NOTE: no memory is allocated on GPU yet, only an identifier
        self.gpu_id = glGenTextures(1)

        # All next configuring commands will affect this newly created texture object
        glBindTexture(self.target, self.gpu_id)

        # Send the texture data from CPU to GPU
        if is_1d:
            assert self.height == 1
            glTexImage1D(self.target,
                0,
                GL_RGBA,
                self.width,
                0,
                cpu_format,
                GL_UNSIGNED_BYTE,
                np.ascontiguousarray(cpu_image).flatten()
            )
        else:
            glTexImage2D(self.target,
                0,       # mip-map level we're filling in
                GL_RGBA, # how on GPU the data will be layed out
                self.width, self.height,
                0,      # always 0
                cpu_format, # how on CPU we stored the `pixels` array
                GL_UNSIGNED_BYTE, # which type of all values is in the `pixels` array
                np.ascontiguousarray(cpu_image).flatten(), # array of channels for all pixels
            )

        # Function `glTexParameteri` sets 1 parameter value
        # The arguments mean : texture_type, parameter_name, parameter_value

        # if the texture is accessed outside coordinates [0; 1],
        # the values will repeat, e.g. coordinate 2.3 will be equivalent to 0.3
        # other options: GL_MIRRORED_REPEAT, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_BORDER
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # TODO: text filtering
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # TODO: text mipmaps
        glGenerateMipmap(self.target)

    def __del__(self):
        if getattr(self, 'gpu_id', None):
            glDeleteTextures(np.array([self.gpu_id], dtype=np.uint32))