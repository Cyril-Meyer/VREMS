from OpenGL.GL import shaders
from OpenGL.GL import *


def load_shader(shader_file):
    shader_source = ""
    with open(shader_file) as f:
        shader_source = f.read()
    f.close()
    return str.encode(shader_source)


def compile_shader(vs, fs):
    vertex_shader = load_shader(vs)
    fragment_shader = load_shader(fs)

    shader = shaders.compileProgram(shaders.compileShader(vertex_shader,
                                                          GL_VERTEX_SHADER),
                                    shaders.compileShader(fragment_shader,
                                                          GL_FRAGMENT_SHADER))
    return shader


def compile_shader_geometry(vs, fs, gs):
    print("compile start")
    vertex_shader = load_shader(vs)
    fragment_shader = load_shader(fs)
    geom_shader = load_shader(gs)

    shader = glCreateProgram()

    vertex = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    glAttachShader(shader, vertex)
    siv = glGetShaderiv(vertex, GL_COMPILE_STATUS)
    print(siv)
    print("vertex compiled")
    # print(glGetShaderInfoLog(vertex))
    fragment = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    glAttachShader(shader, fragment)
    siv = glGetShaderiv(fragment, GL_COMPILE_STATUS)
    print(siv)
    print("fragment compiled")
    geometry = shaders.compileShader(geom_shader, GL_GEOMETRY_SHADER)
    glAttachShader(shader, geometry)
    siv = glGetShaderiv(geometry, GL_COMPILE_STATUS)
    print(siv)
    print("geometry compiled")
    glLinkProgram(shader)
    piv = glGetProgramiv(shader, GL_LINK_STATUS)
    print(glGetProgramInfoLog(shader))
    print("program linked")
    print(piv)
    glValidateProgram(shader)
    glDetachShader(shader, vertex)
    glDetachShader(shader, fragment)
    glDetachShader(shader, geometry)
    print("shaders detached")
    glDeleteShader(vertex)
    glDeleteShader(fragment)
    glDeleteShader(geometry)
    print("shaders deleted")
    # glUseProgram(shader)
    print("compile end")
    return shader
