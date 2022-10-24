from ..common.gpu_texture import GpuTexture
from ..common.gpu_shader import GpuShader
from ..common.gpu_mesh import GpuMesh
from ..base_demo import BaseDemo
from ..common.defines import *
from OpenGL.GL import *
from PIL import Image, ImageCms
import io
import glfw
import pyrr
import numpy as np
import imgui

def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

class Lecture02_ProjectionDemo(BaseDemo):
    def __init__(self):
        super().__init__(ui_defaults=None)
        self.reset_camera()
        self.ui_width_height_proportional = True
        self.is_perspective = False # orthogonal by default
        self.is_extra_visualization_enabled = False

    def reset_camera(self):
        self.proj_bottom, self.proj_top = -1, 1
        self.proj_left, self.proj_right = -1, 1
        self.proj_near, self.proj_far = -1, 1

    def load(self, window):
        super().load(window)

        self.shader = GpuShader('vert.glsl', 'frag.glsl', out_variable=b'out_color')
        shader_id = self.shader.use()
        position_shader_location = glGetAttribLocation(shader_id, "a_position")
        texcoord_shader_location = glGetAttribLocation(shader_id, "a_texture_coords")

        self.scene = GpuMesh(obj_filepath='../../assets/monkeys_grid.obj', use_index_buffer=True)
        self.scene.with_attributes_size(position_n_coords=3, texcoord_n_coords=2, normals_n_coords=0)
        self.scene.with_attributes_shader_location(position_shader_location, texcoord_shader_location, normals_location=None)
        self.scene.build(verbose=False)

        self.texture = GpuTexture(cpu_image=Image.open('../../assets/palette_contrast.png'), flip_y=True)
        self.texture.use(texture_unit=0)

        self.make_extra_visualizations()

        # enable Z-buffer
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        self.is_loaded = True

    def make_extra_visualizations(self):
        camera_projection = self.get_perspective_matrix(-1, 1, -1, 1, 0.01, 100.0)
        camera_view = pyrr.Matrix44.look_at((0,0,-2), (0,0,0), (0,1,0), dtype=np.float32)
        self.side_view_transform = camera_projection @ camera_view
        # frustum mesh

    def render_extra_visualizations(self):
        pass

    def get_orthogonal_matrix(self, left, right, top, bottom, near, far):
        """ Analogous to calling
            pyrr.Matrix44.orthogonal_projection(left, right, top, bottom, near, far, dtype=np.float32)"""
        width  = right - left
        height = top - bottom
        depth  = far - near
        return np.ascontiguousarray([
                      2/width,                      0,                   0, 0,
                            0,               2/height,                   0, 0,
                            0,                      0,            -2/depth, 0,
        -(right + left)/width, -(top + bottom)/height, -(far + near)/depth, 1,
        ], dtype=np.float32).reshape(4, 4)

    def get_perspective_matrix(self, left, right, bottom, top, near, far):
        """ Analogous to calling
            pyrr.Matrix44.perspective_projection_bounds(left, right, top, bottom, near, far, dtype=np.float32)"""
        width  = right - left
        height = top - bottom
        depth  = far - near
        return np.ascontiguousarray([
                     2*near/width,                      0,                   0,  0,
                                0,          2*near/height,                   0,  0,
             (right + left)/width,  (top + bottom)/height, -(far + near)/depth, -1,
                                0,                      0,   -2*near*far/depth,  0,
        ], dtype=np.float32).reshape(4, 4)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        glClearColor(0.0,0.0,0.0,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader_id = self.shader.use()
        uniform_aspect = glGetUniformLocation(shader_id, "u_aspect_ratio")
        aspect_ratio = width / height
        glUniform1f(uniform_aspect, aspect_ratio)

        if not self.is_extra_visualization_enabled:
            if self.is_perspective:
                projection_fn = self.get_perspective_matrix
            else:
                projection_fn = self.get_orthogonal_matrix

            projection = projection_fn(
                    self.proj_left  , self.proj_right,
                    self.proj_top   , self.proj_bottom,
                    self.proj_near  , self.proj_far)
        else:
            projection = self.side_view_transform

        uniform_transform = glGetUniformLocation(shader_id, "u_transform")
        glUniformMatrix4fv(uniform_transform, 1, GL_FALSE, projection)

        self.scene.use()
        glDrawElements(GL_TRIANGLES, self.scene.n_draw_elements, GL_UNSIGNED_INT, None)

    def keyboard_callback(self, window, key, scancode, action, mods):
        super().keyboard_callback(window, key, scancode, action, mods)
        if action not in [glfw.PRESS, glfw.REPEAT]:
            return

        if key == glfw.KEY_R:
            self.reset_camera()
        elif key == glfw.KEY_Q:
            self.is_perspective = not self.is_perspective

    def unload(self):
        if not self.is_loaded:
            return
        self.is_loaded = False
        glUseProgram(0)
        glDisable(GL_DEPTH_TEST)
        del self.shader
        del self.scene
        del self.texture
        super().unload()


    def render_ui(self):
        imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
        imgui.set_next_window_position(0, 0, condition=imgui.FIRST_USE_EVER)
        imgui.begin("Info", closable=True, flags=imgui.WINDOW_NO_FOCUS_ON_APPEARING)
        imgui.text('FPS: %.2f' % imgui.get_io().framerate)
        imgui.end()

        min_range, max_range = -10, 10
        imgui.begin("Controls", closable=True, flags=imgui.WINDOW_NO_FOCUS_ON_APPEARING)
        _, self.ui_width_height_proportional = imgui.checkbox("Width and height are proportional", self.ui_width_height_proportional)
        if imgui.button('Reset camera'):
            self.reset_camera()
        imgui.same_line()
        if imgui.button('Mode'):
            self.is_perspective = not self.is_perspective
        imgui.same_line()
        imgui.text("Perspective projection" if self.is_perspective else "Orthogonal projection")

        imgui.columns(2, '')
        _, candidate_bottom = imgui.slider_float('Bottom', self.proj_bottom, min_range, max_range, '%.3f')
        if candidate_bottom > self.proj_top-1e-3:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            imgui.text("Clamped to Top")
            imgui.pop_style_color(1)
        self.proj_bottom = min(candidate_bottom, self.proj_top-1e-3)
        imgui.next_column()

        _, candidate_top =  imgui.slider_float('Top', self.proj_top, min_range, max_range, '%.3f', power=1.0)
        if candidate_top < self.proj_bottom+1e-3:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            imgui.text("Clamped to Bottom")
            imgui.pop_style_color(1)
        self.proj_top = max(candidate_top, self.proj_bottom+1e-3)
        imgui.next_column()

        if not self.ui_width_height_proportional:
            _, candidate_left = imgui.slider_float('Left', self.proj_left, min_range, max_range, '%.3f')
            if candidate_left > self.proj_right-1e-3:
                imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
                imgui.text("Clamped to Right")
                imgui.pop_style_color(1)
            self.proj_left = min(candidate_left, self.proj_right-1e-3)
            imgui.next_column()

            _, candidate_right =  imgui.slider_float('Right', self.proj_right, min_range, max_range, '%.3f', power=1.0)
            if candidate_right < self.proj_left+1e-3:
                imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
                imgui.text("Clamped to Left")
                imgui.pop_style_color(1)
            self.proj_right = max(candidate_right, self.proj_left+1e-3)
            imgui.next_column()
        else:
            self.proj_left  = min(candidate_bottom, self.proj_right-1e-3)
            self.proj_right = max(candidate_top, self.proj_left+1e-3)

        min_range, max_range = -1.5, 3
        _, candidate_near = imgui.slider_float('Near', self.proj_near, min_range, max_range, '%.3f', power=10.0)
        if candidate_near > self.proj_far-1e-3:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            imgui.text("Clamped to Far")
            imgui.pop_style_color(1)
        self.proj_near = min(candidate_near, self.proj_far-1e-3)
        imgui.next_column()

        _, candidate_far =  imgui.slider_float('Far', self.proj_far, min_range, max_range, '%.3f', power=1.0)
        if candidate_far < self.proj_near+1e-3:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            imgui.text("Clamped to Near")
            imgui.pop_style_color(1)
        self.proj_far = max(candidate_far, self.proj_near+1e-3)
        imgui.next_column()

        _, self.is_extra_visualization_enabled = imgui.checkbox(
            "3rd person view", self.is_extra_visualization_enabled)

        imgui.end()





