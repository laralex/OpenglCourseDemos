from dataclasses import dataclass
from ..common.gpu_shader import GpuShader
from ..demos_loader import Demo
from ..common.defines import *
from OpenGL.GL import *
import PIL
import numpy as np

@dataclass
class UiDefaults:
    color: int

class Lecture01_TextureDemo(Demo):
    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def load(self, window):
        super().load(window)
        self.make_shader()
        self.make_vertex_data()
        self.is_loaded = True

    def make_shader(self):
        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')

        # The fragrament shader uses rasterized texture coordinates `v_texcoord`
        # connect texture and the shader, so that we can render pixels with texture values

        self.texture_id = self.make_gpu_texture('../../assets/crate_color.jpeg')

        self.shader.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        uniform_texture = glGetUniformLocation(self.shader.shader_program, "u_texture")
        glUniform1i(uniform_texture, 0)

    def make_gpu_texture(self, image_path):
        cpu_image = PIL.Image.open(image_path)
        width, height = cpu_image.size
        target = GL_TEXTURE_2D
        # OpenGL creates a unique texture identifier (just a number) on its GPU side
        # and returns it to our CPU-side code, it's a cheap way for us 
        # to communicate to GPU which texture among all we want to use
        # ! NOTE: no memory is allocated on GPU yet, only an identifier
        gpu_id = glGenTextures(1)

        # All next configuring commands will affect this newly created texture object
        glBindTexture(target, gpu_id)

        # Send the texture data from CPU to GPU
        glTexImage2D(target,
            0,       # mip-map level we're filling in
            GL_RGB, # how on GPU the data will be layed out
            width, height,
            0,      # always 0
            GL_RGB, # how on CPU we stored the `pixels` array
            GL_UNSIGNED_BYTE, # which type of all values is in the `pixels` array
            np.ascontiguousarray(cpu_image).flatten(), # array of channels for all pixels
        )

        # Function `glTexParameteri` sets 1 parameter value
        # The arguments mean : texture_type, parameter_name, parameter_value

        # if the texture is accessed outside coordinates [0; 1],
        # the values will repeat, e.g. coordinate 2.3 will be equivalent to 0.3
        # other options: GL_REPEAT, GL_MIRRORED_REPEAT, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_BORDER
        glTexParameteri(target, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(target, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glGenerateMipmap(target)
        return gpu_id

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

        texture_coords *= 2.5

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

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)


    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False

        glDeleteVertexArrays(1, np.asarray([self.vao], dtype=np.uint32))
        glDeleteBuffers(2, np.asarray([self.gpu_positions, self.gpu_texture_coords], dtype=np.uint32))
        glDeleteTextures(np.array([self.texture_id], dtype=np.uint32))
        del self.shader
        del self.vao, self.gpu_positions, self.gpu_texture_coords
        super().unload()
        # TODO: delete texture





