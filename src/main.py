from dataclasses import dataclass
import math
from threading import Thread
from typing import Callable

import glfw
import OpenGL.GL as gl

from threading import Thread

from dpgext.utils.logger import LOGGER

from constants import WINDOW_SIZE
from app_state import STATE
from gui import AppGui

import numpy as np

import keyboard

def create_window():
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    window = glfw.create_window(*WINDOW_SIZE, "Simple Window", monitor=None, share=None)
    glfw.make_context_current(window)
    glfw.show_window(window)
    return window

def glfw_thread():
    window = create_window()

    # TODO: code to draw the scene in a framebuffer and send it to the dearpygui window
    # fbo = gl.glGenFramebuffers(1)
    # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
    # #TODO: glDeleteFramebuffers(1, &frameBuffer);


    # gl_tex_id = gl.glGenTextures(1)
    # gl.glBindTexture(gl.GL_TEXTURE_2D, gl_tex_id)
    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, *WINDOW_SIZE, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)

    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    # gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, 0, 0)


    vertex_shader = """
    #version 330
    in vec2 position;
    uniform mat4 mvp;
    void main() {
        gl_Position = vec4(position, 0.0, 1.0) * mvp;
    }
    """

    fragment_shader = """
    #version 330
    void main() {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
    """

    program = gl.glCreateProgram()
    vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    gl.glShaderSource(vertex, vertex_shader)
    gl.glShaderSource(fragment, fragment_shader)

    gl.glCompileShader(vertex)
    
    gl.glCompileShader(fragment)

    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)

    gl.glLinkProgram(program)

    gl.glUseProgram(program)
    # return

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)

    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

    vertices = [
        0.0,  0.866025403784-0.5+0.183012701892, 0.0,
        0.5, -0.5+0.183012701892, 0.0,
        -0.5, -0.5+0.183012701892, 0.0
    ]
    # Set the vertex buffer data
    gl.glBufferData(gl.GL_ARRAY_BUFFER, len(vertices)*4, (gl.GLfloat * len(vertices))(*vertices), gl.GL_STATIC_DRAW)

    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    
    gl.glEnableVertexAttribArray(1)
    gl.glVertexAttribPointer(1, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    mvp_loc = gl.glGetUniformLocation(program, 'mvp')

    while not glfw.window_should_close(window) and not STATE.closing:
        glfw.poll_events()

        gl.glUniformMatrix4fv(mvp_loc, 1, gl.GL_FALSE, STATE.mvp_manager.mvp)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(1.0, 1.0, 1.0, 1.0)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        # Draw the triangle
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)


        glfw.swap_buffers(glfw.get_current_context())
    
    LOGGER.log_info("GLFW thread is closing", 'glfw_thread')
    STATE.closing = True

def register_keyboard_controls():
    TRANSLATION_STEP = 0.04
    ROTATION_STEP = 2*math.pi/360 * 5
    SCALE_STEP = 0.2

    def callback_gen(step: float, callback: Callable[[float], None]):
        # if shift is pressed, the step is increased
        def callback_wrapper(*_args):
            print(f"shift is pressed: {keyboard.is_pressed('shift')}")
            if keyboard.is_pressed('shift'):
                callback(step * 2)
            elif keyboard.is_pressed('ctrl'):
                callback(step / 2)
            else:
                callback(step)
        
        return callback_wrapper


    keyboard.on_press_key('w', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(0.0, step)))
    keyboard.on_press_key('s', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(0.0, -step)))
    keyboard.on_press_key('a', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(-step, 0.0)))
    keyboard.on_press_key('d', callback_gen(TRANSLATION_STEP, lambda step: STATE.mvp_manager.translate(step, 0.0)))
    keyboard.on_press_key('q', callback_gen(ROTATION_STEP, lambda step: STATE.mvp_manager.rotate(step)))
    keyboard.on_press_key('e', callback_gen(ROTATION_STEP, lambda step: STATE.mvp_manager.rotate(-step)))
    keyboard.on_press_key('z', callback_gen(SCALE_STEP, lambda step: STATE.mvp_manager.zoom(step)))
    keyboard.on_press_key('x', callback_gen(SCALE_STEP, lambda step: STATE.mvp_manager.zoom(-step)))

def main():
    register_keyboard_controls()

    LOGGER.log_info("Starting app", 'main')

    LOGGER.log_trace("Init Glfw", 'main')
    glfw.init()
    
    LOGGER.log_trace("Init GUI", 'main')
    gui = AppGui()

    LOGGER.log_trace("Start GLFW thread", 'main')
    t = Thread(target=glfw_thread)
    t.start()

    LOGGER.log_trace("Start GUI", 'main')
    gui.run()

    LOGGER.log_info("GUI Has been closed, waiting for GLFW to close...", 'main')
    t.join()
    LOGGER.log_info("GLFW thread has been closed", 'main')

    LOGGER.log_trace("Terminating Glfw", 'main')
    glfw.terminate()
    LOGGER.log_info("App has been closed gracefully", 'main')

if __name__ == "__main__":
    main()