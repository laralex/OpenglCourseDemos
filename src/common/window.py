import glfw
import sys

def glfw_create_window(window_name, window_size=(512, 512)):
    width, height = window_size
    window = glfw.create_window(width, height, window_name, monitor=None, share=None)

    # Configure window to work with OpenGL version 3.3
    glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Single buffer mode:
    # - OpenGL allocates 1 memory storage
    # - Every drawing OpenGL command updates this memory
    # - On every refresh of your physical screen, this memory's current content is visualized
    # ! Consequence - the user might occasionally see an unfinished drawing

    # Double buffer mode:
    # - 2 separate memory storages are held by OpenGL, also called "front" and "back" buffers
    # - The drawing commands change the "back" buffer
    # - The screen receives the content of the "front" buffer
    # - When you're finished drawing to the back buffer, you should call a buffer swapping command
    # - After that OpenGL simply swaps pointers to memory locations (a very cheap operation),
    #   thus the content of the back buffer becomes the front buffer and gets visualized
    glfw.window_hint(glfw.DOUBLEBUFFER, True)

    if sys.platform.startswith('darwin'):
        # For operating systems from Apple
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

    return window

def glfw_is_fullscreen(window):
    monitor = glfw.get_window_monitor(window)
    return bool(monitor)

def glfw_switch_fullscreen(window, enable_fullscreen, window_position=None, window_size=None):
    # already switched
    if enable_fullscreen == glfw_is_fullscreen(window):
        return

    if enable_fullscreen: # make fullscreen
        monitor = glfw.get_primary_monitor()
        video_mode = glfw.get_video_mode(monitor)
        glfw.window_hint(glfw.RED_BITS, video_mode.bits.red)
        glfw.window_hint(glfw.GREEN_BITS, video_mode.bits.green)
        glfw.window_hint(glfw.BLUE_BITS, video_mode.bits.blue)
        glfw.window_hint(glfw.REFRESH_RATE, video_mode.refresh_rate)
        glfw.set_window_monitor(window, monitor, 0, 0, video_mode.size.width, video_mode.size.height, video_mode.refresh_rate)
    else: # make windowed
        x, y = window_position
        width, height = window_size
        glfw.set_window_monitor(window, None, x, y, width, height, 0)

def glfw_set_input_callbacks(window, keyboard_callback, mouse_button_callback, mouse_scroll_callback):
    # allows to write custom reaction to pressing of keyboard buttons,
    # mouse buttons, mouse scroll wheel
    if keyboard_callback is not None:
        glfw.set_key_callback(window, keyboard_callback)
    if mouse_button_callback is not None:
        glfw.set_mouse_button_callback(window, mouse_button_callback)
    if mouse_scroll_callback is not None:
        glfw.set_scroll_callback(window, mouse_scroll_callback)

def glfw_set_window_callbacks(window, window_size_callback):
    # allows to write custom reaction to window events: resizing, dragging,
    # minimizing, maximizing, etc
    if window_size_callback is not None:
        glfw.set_window_size_callback(window, window_size_callback)




