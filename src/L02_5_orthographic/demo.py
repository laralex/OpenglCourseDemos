from ..common.gpu_texture import GpuTexture
from ..common.gpu_shader import GpuShader
from ..common.gpu_mesh import GpuMesh
from ..demos_loader import Demo
from ..common.defines import *
from OpenGL.GL import *
from PIL import Image, ImageCms
import io
import glfw
import pyrr
import numpy as np

def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

class Lecture02_OrthographicDemo(Demo):
    def __init__(self):
        super().__init__(ui_defaults=None)
        self.reset_camera()
    
    def reset_camera(self):
        self.ortho_bottom, self.ortho_top = -1, 1
        self.ortho_left, self.ortho_right = -1, 1
        self.ortho_near, self.ortho_far = -1, 1

    def load(self, window):
        super().load(window)

        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')
        shader_id = self.shader.use()
        position_shader_location = glGetAttribLocation(shader_id, "a_position")
        texcoord_shader_location = glGetAttribLocation(shader_id, "a_texture_coords")

        self.scene = GpuMesh(obj_filepath='../../assets/blocks_grid.obj', use_index_buffer=True)
        self.scene.with_attributes_size(position_n_coords=3, texcoord_n_coords=2, normals_n_coords=0)
        self.scene.with_attributes_shader_location(position_shader_location, texcoord_shader_location, normals_location=None)
        self.scene.build(verbose=False)

        self.texture = GpuTexture(cpu_image=convert_to_srgb(Image.open('../../assets/palette_contrast.png')))
        self.texture.use(texture_unit=0)

        # enable Z-buffer
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        self.is_loaded = True


    def get_orthogonal_matrix(self, left, right, bottom, top, near, far):
        """ Analogous to calling
            pyrr.Matrix44.orthogonal_projection(left, right, bottom, top, near, far, dtype=np.float32)"""
        width  = right - left
        height = top - bottom
        depth  = far - near
        return np.ascontiguousarray([
                      2/width,                      0,                   0, 0,
                            0,               2/height,                   0, 0,
                            0,                      0,            -2/depth, 0,
        -(right + left)/width, -(top + bottom)/height, -(far + near)/depth, 1,
        ], dtype=np.float32)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0.0,0.0,0.0,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        aspect_ratio = width / height
        glUniform1f(uniform_aspect, aspect_ratio)

        orthographic_projection = self.get_orthogonal_matrix(
            self.ortho_left  , self.ortho_right,
            self.ortho_bottom, self.ortho_top,
            self.ortho_near  , self.ortho_far)

        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, orthographic_projection)

        self.scene.use()
        glDrawElements(GL_TRIANGLES, self.scene.n_draw_elements, GL_UNSIGNED_INT, None)

    def keyboard_callback(self, window, key, scancode, action, mods):
        super().keyboard_callback(window, key, scancode, action, mods)
        DELTA=0.02
        if action not in [glfw.PRESS, glfw.REPEAT]:
            return

        if key == glfw.KEY_W:
            self.ortho_top += DELTA
        elif key == glfw.KEY_S:
            self.ortho_bottom -= DELTA
        elif key == glfw.KEY_D:
            self.ortho_right += DELTA
        elif key == glfw.KEY_A:
            self.ortho_left -= DELTA
        elif key == glfw.KEY_Q:
            self.ortho_far += DELTA
        elif key == glfw.KEY_E:
            self.ortho_near -= DELTA
        elif key == glfw.KEY_R:
            self.reset_camera()

    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glDisable(GL_DEPTH_TEST)
        del self.shader
        del self.scene
        del self.texture
        super().unload()





