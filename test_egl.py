import glfw
from OpenGL import GL

def main():
    # Initialize GLFW
    
    glfw.set_error_callback(lambda error, desc: print(f"[GLFW ERROR] ({error}): {desc.decode()}"))

    if not glfw.init():
        raise RuntimeError("GLFW init failed")

    # Force native GLX context (instead of EGL)
    glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
    glfw.window_hint(glfw.CONTEXT_CREATION_API, glfw.NATIVE_CONTEXT_API)
    glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)

    # Create a visible window
    window = glfw.create_window(800, 600, "GLX + Mesa Test", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

    glfw.make_context_current(window)

    # Query and print OpenGL info
    version = GL.glGetString(GL.GL_VERSION)
    renderer = GL.glGetString(GL.GL_RENDERER)
    vendor = GL.glGetString(GL.GL_VENDOR)

    print("✅ OpenGL context created with GLX (via Mesa)")
    print("OpenGL Version:", version.decode() if version else "None")
    print("Renderer:", renderer.decode() if renderer else "None")
    print("Vendor:", vendor.decode() if vendor else "None")
    print("🪟 You should see a visible OpenGL window. Close it to exit.")

    # Event loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
