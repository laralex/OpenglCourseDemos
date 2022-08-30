import glfw

class GlfwInstance:
    '''
    A Python context, only inside of which the GLFW commands can be called, e.g.
    with GlfwInstance():
        ...
        <glfw commands are allowed here>
        ...
    <glfw commands with fail here>
    '''
    def __enter__(self):
        if not glfw.init():
            raise SystemError("Can't initialize windowing library GLFW")
        return glfw

    def __exit__(self, type, value, traceback):
        glfw.terminate()

def glfw_is_fullscreen(window):
    return glfw.get_window_monitor(window)

def glfw_set_input_callbacks(window, keyboard_callback, mouse_button_callback, mouse_scroll_callback):
    if keyboard_callback is not None:
        glfw.set_key_callback(window, keyboard_callback)
    if mouse_button_callback is not None:
        glfw.set_mouse_button_callback(window, mouse_button_callback)
    if mouse_scroll_callback is not None:
        glfw.set_scroll_callback(window, mouse_scroll_callback)

def glfw_create_window(window_name, window_size=(512, 512)):
    width, height = window_size
    window = glfw.create_window(width, height, window_name, monitor=None, share=None)

    glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.DOUBLEBUFFER, True)

    return window

def glfw_set_borderless_fullscreen(window, enable_fullscreen, window_position=None, window_size=None):
    if enable_fullscreen == glfw_is_fullscreen(window):
        return
    if enable_fullscreen:
        monitor = glfw.get_primary_monitor()
        video_mode = glfw.get_video_mode(monitor)
        glfw.window_hint(glfw.RED_BITS, video_mode.bits.red)
        glfw.window_hint(glfw.GREEN_BITS, video_mode.bits.green)
        glfw.window_hint(glfw.BLUE_BITS, video_mode.bits.blue)
        glfw.window_hint(glfw.REFRESH_RATE, video_mode.refresh_rate)
        glfw.set_window_monitor(window, monitor, 0, 0, video_mode.size.width, video_mode.size.height, video_mode.refresh_rate)
    else:
        x, y = window_position
        width, height = window_size
        glfw.set_window_monitor(window, None, x, y, width, height, 0)

def glfw_set_window_callbacks(window, window_size_callback):
    if window_size_callback is not None:
        glfw.set_window_size_callback(window, window_size_callback)

