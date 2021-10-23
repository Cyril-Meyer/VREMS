import numpy as np

import glfw
from OpenGL.GL import *
from pyrr import matrix44, Matrix44, Vector3

import shader


def render_segmentation(image, labels, labels_colors):
    scene_center = [image.shape[0] / 2, image.shape[1] / 2, image.shape[2] / 2]

    # initialization of GLFW
    if not glfw.init():
        return

    # todo : resizable
    glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
    glfw.window_hint(glfw.SAMPLES, 8)
    w_width, w_height = 1000, 800
    window = glfw.create_window(w_width, w_height, "VREMS", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    glfw.swap_interval(1)
    voxel_shader = shader.compile_shader_geometry("shaders/voxel_vertex_shader.vs",
                                                  "shaders/voxel_frag_shader.fs",
                                                  "shaders/voxel_geo_shader.gs")
    slice_shader = shader.compile_shader("shaders/slice_vertex_shader.vs",
                                         "shaders/slice_frag_shader.fs")

    # slice plane
    vertices = [0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, image.shape[2], 1.0, 0.0,
                image.shape[0], 0.0, image.shape[2], 1.0, 1.0,
                image.shape[0], 0.0, 0.0, 0.0, 1.0]

    vertices = np.array(vertices, dtype=np.float32)

    indices = [0, 1, 2,
               0, 2, 3]
    indices = np.array(indices, dtype=np.uint32)

    # geometry data

    VAOS = glGenVertexArrays(1)
    glBindVertexArray(VAOS)

    VBOS = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBOS)
    glBufferData(GL_ARRAY_BUFFER, vertices.itemsize * len(vertices), vertices, GL_STATIC_DRAW)

    EBOS = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBOS)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)

    positionS = glGetAttribLocation(slice_shader, "position")
    glVertexAttribPointer(positionS, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(0))
    glEnableVertexAttribArray(positionS)

    texCoord = glGetAttribLocation(slice_shader, "inTexCoord")
    glVertexAttribPointer(texCoord, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(12))
    glEnableVertexAttribArray(texCoord)

    array_nb_voxels = []
    array_vertex_array_object = []

    for label in labels:
        array_nb_voxels.append(np.sum(label))
        voxels = np.argwhere(label).flatten().astype(np.float32)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, voxels.itemsize * len(voxels), voxels, GL_STATIC_DRAW)

        position = glGetAttribLocation(voxel_shader, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, voxels.itemsize * 3, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        array_vertex_array_object.append(vao)

    glClearColor(0.5, 0.5, 0.5, 1.0)
    glEnable(GL_DEPTH_TEST)

    previous = glfw.get_time()
    current = glfw.get_time()

    # camera = Camera()
    # camera.translate(Vector3([0.0, 0.0, -1000.0]))
    # # camera.look_at(camera.m_pos, Vector3([0, 0, 0]), camera.m_up)
    # camera.update()
    model = matrix44.create_from_translation(Vector3([0.0, 0.0, 0.0]))
    # view = matrix44.create_from_translation(Vector3([0, 0,  -1000]))
    # view = camera.getViewMatrix()
    view = matrix44.create_look_at(Vector3([0, 500, -1000]), Vector3([0, -0.72, 0.72]), Vector3([0, 0.72, -0.72]))
    projection = matrix44.create_perspective_projection_matrix(45.0, w_width / w_height, 0.1, 1500.0)

    glUseProgram(voxel_shader)
    #  voxel shader uniforms
    view_loc_voxel = glGetUniformLocation(voxel_shader, "view")
    proj_loc_voxel = glGetUniformLocation(voxel_shader, "projection")
    model_loc_voxel = glGetUniformLocation(voxel_shader, "model")
    label_color_loc_voxel = glGetUniformLocation(voxel_shader, "label_color")
    voxel_size_loc_voxel = glGetUniformLocation(voxel_shader, "size_voxel")
    max_height_loc_voxel = glGetUniformLocation(voxel_shader, "max_height")
    center_loc_voxel = glGetUniformLocation(voxel_shader, "center")

    glUniformMatrix4fv(view_loc_voxel, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc_voxel, 1, GL_FALSE, projection)
    glUniform1f(voxel_size_loc_voxel, 1)
    glUniform3f(center_loc_voxel, scene_center[0], scene_center[1], scene_center[2])

    glUseProgram(slice_shader)
    #  slice shader uniforms
    view_loc_slice = glGetUniformLocation(slice_shader, "view")
    proj_loc_slice = glGetUniformLocation(slice_shader, "projection")
    model_loc_slice = glGetUniformLocation(slice_shader, "model")
    max_height_loc_slice = glGetUniformLocation(slice_shader, "max_height")
    center_loc_slice = glGetUniformLocation(slice_shader, "center")

    glUniformMatrix4fv(view_loc_slice, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc_slice, 1, GL_FALSE, projection)
    glUniform3f(center_loc_slice, scene_center[0], scene_center[1], scene_center[2])

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    count = 0
    countdown = 1
    resave = True
    redisplay = True
    while not glfw.window_should_close(window):
        if redisplay:
            # redisplay = False
            # import time
            # time.sleep(1/10)
            # glfw.wait_events()
            glClearColor(0.15, 0.15, 0.15, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glPolygonMode(GL_FRONT, GL_FILL)

            rot = matrix44.create_from_y_rotation(0.2 * glfw.get_time())
            model = matrix44.create_from_translation(Vector3([0.0, 0.0, 0.0]))
            model = matrix44.multiply(model, rot)

            glBindTexture(GL_TEXTURE_2D, texture)
            image_data = image[:, count - countdown + 1, :]
            image_data = image_data.flatten().astype(np.float32)
            # image_data = image_data[::2]
            # print(image_data, image_data.shape)
            # img_data = numpy.array(list(image.getdata()), numpy.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, image.shape[0], image.shape[2], 0, GL_RED, GL_FLOAT, image_data)

            glUseProgram(slice_shader)
            glActiveTexture(GL_TEXTURE0)
            glBindVertexArray(VAOS)
            glBindTexture(GL_TEXTURE_2D, texture)
            glUniformMatrix4fv(model_loc_slice, 1, GL_FALSE, model)
            glUniform1f(max_height_loc_slice, count - countdown)
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
            glBindTexture(GL_TEXTURE_2D, 0)

            glUseProgram(voxel_shader)
            glUniformMatrix4fv(model_loc_voxel, 1, GL_FALSE, model)
            glUniform1f(max_height_loc_voxel, count)

            for i in range(len(labels)):
                glBindVertexArray(array_vertex_array_object[i])
                glUniform4f(label_color_loc_voxel,
                            labels_colors[i][0],
                            labels_colors[i][1],
                            labels_colors[i][2],
                            labels_colors[i][3])
                glDrawArrays(GL_POINTS, 0, array_nb_voxels[i])

            glfw.swap_buffers(window)
            count += int(count < image.shape[1] - 1)
            countdown += int((count >= image.shape[1] - 1) and (countdown <= image.shape[1] - 1))

        glfw.poll_events()

    glfw.terminate()
    return


def window_resize(window, width, height):
    if width > height:
        size = height
    else:
        size = width

    glViewport(0, 0, width, height)
    return
