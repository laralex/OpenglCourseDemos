from OpenGL.GL import *
import os

class GpuShader:
    def __init__(self, vertex_shader_code: str, fragment_shader_code: str, out_variable: bytes):
        if os.path.isfile(vertex_shader_code):
            vertex_shader_code = read_text_file(vertex_shader_code)
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, vertex_shader_code)
        glCompileShader(self.vertex_shader)

        if os.path.isfile(fragment_shader_code):
            fragment_shader_code = read_text_file(fragment_shader_code)
        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, fragment_shader_code)
        glCompileShader(self.fragment_shader)

        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vertex_shader)
        glAttachShader(self.shader_program, self.fragment_shader)

        glBindFragDataLocation(self.shader_program, 0, out_variable)
        glLinkProgram(self.shader_program)

        self.check_shader_compilation()

    def __del__(self):
        glDeleteProgram(self.shader_program)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

    def use(self) -> int:
        glUseProgram(self.shader_program)
        return self.shader_program

    def check_shader_compilation(self):
        if not glGetShaderiv(self.vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(self.vertex_shader)
            raise Exception(f"Vertex shader didn't compile with error: {error}")
        if not glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(self.fragment_shader)
            raise Exception(f"Fragment shader didn't compile with error: {error}")
        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.shader_program)
            raise Exception(f"Shader program didn't compile with error: {error}")

def read_text_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()