import numpy as np

import glfw
from OpenGL.GL import *
from pyrr import matrix44, Matrix44, Vector3, vector
from PIL import Image
import cv2

import shader


def render_segmentation(image,
                        labels,
                        labels_colors,
                        background_color=(0.15, 0.15, 0.15, 1.0),
                        capture=None,
                        output=None,
                        video_fps=24,
                        view_distance=1.5,
                        rotation_speed=1.0,
                        only_image=False):
    # capture = None : no capture
    # capture = 0 : capture each frame as a png
    # capture > 0 : capture N frame in a video
    # capture_img contain image for video capture if
    if capture is not None:
        capture_img = []

    # todo : alpha only image
    alpha_image = 0.8

    # compute scene center point
    scene_center = [image.shape[0] / 2, image.shape[1] / 2, image.shape[2] / 2]

    # initialization of GLFW
    if not glfw.init():
        return

    glfw.window_hint(glfw.RESIZABLE, GL_TRUE)
    glfw.window_hint(glfw.SAMPLES, 8)
    w_width, w_height = 1000, 800
    window = glfw.create_window(w_width, w_height, "VREMS", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    glfw.swap_interval(1)

    # compile shaders
    voxel_shader = shader.compile_shader_geometry("shaders/voxel_vertex_shader.vs",
                                                  "shaders/voxel_frag_shader.fs",
                                                  "shaders/voxel_geo_shader.gs")
    slice_shader = shader.compile_shader("shaders/slice_vertex_shader.vs",
                                         "shaders/slice_frag_shader.fs")
    texbox_shader = shader.compile_shader("shaders/texbox_vertex_shader.vs",
                                          "shaders/texbox_frag_shader.fs")

    # slice plane
    slice_vertices, texbox0_vertices, texbox1_vertices, texbox2_vertices, texbox3_vertices = get_vertices(image.shape)

    slice_indices = [0, 1, 2,
                     0, 2, 3]
    slice_indices = np.array(slice_indices, dtype=np.uint32)

    # geometry data
    VAOS = glGenVertexArrays(1)
    glBindVertexArray(VAOS)

    VBOS = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBOS)
    glBufferData(GL_ARRAY_BUFFER, slice_vertices.itemsize * len(slice_vertices), slice_vertices, GL_STATIC_DRAW)

    EBOS = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBOS)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, slice_indices.itemsize * len(slice_indices), slice_indices, GL_STATIC_DRAW)

    positionS = glGetAttribLocation(slice_shader, "position")
    glVertexAttribPointer(positionS, 3, GL_FLOAT, GL_FALSE, slice_vertices.itemsize * 5, ctypes.c_void_p(0))
    glEnableVertexAttribArray(positionS)

    texCoord = glGetAttribLocation(slice_shader, "inTexCoord")
    glVertexAttribPointer(texCoord, 2, GL_FLOAT, GL_FALSE, slice_vertices.itemsize * 5, ctypes.c_void_p(12))
    glEnableVertexAttribArray(texCoord)

    position_texbox = glGetAttribLocation(texbox_shader, "position")
    texCoord_texbox = glGetAttribLocation(texbox_shader, "inTexCoord")

    if only_image:
        VAO_texbox0 = glGenVertexArrays(1)
        glBindVertexArray(VAO_texbox0)

        VBO_texbox0 = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_texbox0)
        glBufferData(GL_ARRAY_BUFFER, texbox0_vertices.itemsize * len(texbox0_vertices), texbox0_vertices,
                     GL_STATIC_DRAW)

        EBO_texbox0 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_texbox0)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, slice_indices.itemsize * len(slice_indices), slice_indices,
                     GL_STATIC_DRAW)

        glVertexAttribPointer(position_texbox, 3, GL_FLOAT, GL_FALSE, texbox0_vertices.itemsize * 5, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position_texbox)

        glVertexAttribPointer(texCoord_texbox, 2, GL_FLOAT, GL_FALSE, texbox0_vertices.itemsize * 5,
                              ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoord_texbox)

        VAO_texbox1 = glGenVertexArrays(1)
        glBindVertexArray(VAO_texbox1)

        VBO_texbox1 = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_texbox1)
        glBufferData(GL_ARRAY_BUFFER, texbox1_vertices.itemsize * len(texbox1_vertices), texbox1_vertices,
                     GL_STATIC_DRAW)

        EBO_texbox1 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBOS)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, slice_indices.itemsize * len(slice_indices), slice_indices,
                     GL_STATIC_DRAW)

        glVertexAttribPointer(position_texbox, 3, GL_FLOAT, GL_FALSE, texbox1_vertices.itemsize * 5, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position_texbox)

        glVertexAttribPointer(texCoord_texbox, 2, GL_FLOAT, GL_FALSE, texbox1_vertices.itemsize * 5,
                              ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoord_texbox)

        VAO_texbox2 = glGenVertexArrays(1)
        glBindVertexArray(VAO_texbox2)

        VBO_texbox2 = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_texbox2)
        glBufferData(GL_ARRAY_BUFFER, texbox2_vertices.itemsize * len(texbox2_vertices), texbox2_vertices,
                     GL_STATIC_DRAW)

        EBO_texbox2 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBOS)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, slice_indices.itemsize * len(slice_indices), slice_indices,
                     GL_STATIC_DRAW)

        glVertexAttribPointer(position_texbox, 3, GL_FLOAT, GL_FALSE, texbox2_vertices.itemsize * 5, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position_texbox)

        glVertexAttribPointer(texCoord_texbox, 2, GL_FLOAT, GL_FALSE, texbox2_vertices.itemsize * 5,
                              ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoord_texbox)

        VAO_texbox3 = glGenVertexArrays(1)
        glBindVertexArray(VAO_texbox3)

        VBO_texbox3 = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_texbox3)
        glBufferData(GL_ARRAY_BUFFER, texbox3_vertices.itemsize * len(texbox3_vertices), texbox3_vertices,
                     GL_STATIC_DRAW)

        EBO_texbox3 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBOS)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, slice_indices.itemsize * len(slice_indices), slice_indices,
                     GL_STATIC_DRAW)

        glVertexAttribPointer(position_texbox, 3, GL_FLOAT, GL_FALSE, texbox3_vertices.itemsize * 5, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position_texbox)

        glVertexAttribPointer(texCoord_texbox, 2, GL_FLOAT, GL_FALSE, texbox3_vertices.itemsize * 5,
                              ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoord_texbox)

    array_nb_voxels = []
    array_vertex_array_object = []

    # compute vao & vbo for each label
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

    # camera
    view = place_camera(image.shape[0], image.shape[1], image.shape[2], view_distance)
    projection = get_projection(image.shape[0], image.shape[1], image.shape[2], w_width / w_height, view_distance)

    # voxel shader uniforms
    glUseProgram(voxel_shader)
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

    # slice shader uniforms
    glUseProgram(slice_shader)
    view_loc_slice = glGetUniformLocation(slice_shader, "view")
    proj_loc_slice = glGetUniformLocation(slice_shader, "projection")
    model_loc_slice = glGetUniformLocation(slice_shader, "model")
    max_height_loc_slice = glGetUniformLocation(slice_shader, "max_height")
    center_loc_slice = glGetUniformLocation(slice_shader, "center")

    glUniformMatrix4fv(view_loc_slice, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc_slice, 1, GL_FALSE, projection)
    glUniform3f(center_loc_slice, scene_center[0], scene_center[1], scene_center[2])

    # texbox shader uniforms
    glUseProgram(texbox_shader)
    view_loc_texbox = glGetUniformLocation(texbox_shader, "view")
    proj_loc_texbox = glGetUniformLocation(texbox_shader, "projection")
    model_loc_texbox = glGetUniformLocation(texbox_shader, "model")
    max_height_loc_texbox = glGetUniformLocation(texbox_shader, "max_height")
    center_loc_texbox = glGetUniformLocation(texbox_shader, "center")
    alpha_loc_texbox = glGetUniformLocation(texbox_shader, "alpha")

    glUniform3f(center_loc_texbox, scene_center[0], scene_center[1], scene_center[2])
    glUniform1f(alpha_loc_texbox, alpha_image)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    if only_image:
        texture0 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture0)
        # set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image_data = image[0, :, :]
        image_data = image_data.flatten().astype(np.float32)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, image.shape[2], image.shape[1], 0, GL_RED, GL_FLOAT, image_data)

        texture1 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture1)
        # set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image_data = np.flip(np.rot90(image[:, :, -1]), 0)
        image_data = image_data.flatten().astype(np.float32)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, image.shape[0], image.shape[1], 0, GL_RED, GL_FLOAT, image_data)

        texture2 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture2)
        # set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image_data = np.flip(image[-1, :, :], 1)
        image_data = image_data.flatten().astype(np.float32)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, image.shape[2], image.shape[1], 0, GL_RED, GL_FLOAT, image_data)

        texture3 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture3)
        # set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image_data = np.flip(np.flip(np.rot90(image[:, :, 0]), 0), 1)
        image_data = image_data.flatten().astype(np.float32)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, image.shape[0], image.shape[1], 0, GL_RED, GL_FLOAT, image_data)

    # load image
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    count = 0
    countdown = 1
    redisplay = True
    frame_n = 0

    while not glfw.window_should_close(window):
        frame_n += 1
        if redisplay:
            glClearColor(background_color[0],
                         background_color[1],
                         background_color[2],
                         background_color[2])
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glPolygonMode(GL_FRONT, GL_FILL)

            rot = matrix44.create_from_y_rotation(((rotation_speed * 2 * np.pi) * frame_n) / image.shape[1])
            model = matrix44.create_from_translation(Vector3([0.0, 0.0, 0.0]))
            model = matrix44.multiply(model, rot)
            # camera
            x_cap, y_cap, width_cap, height_cap = glGetDoublev(GL_VIEWPORT)
            view = place_camera(image.shape[0], image.shape[1], image.shape[2], view_distance)
            projection = get_projection(image.shape[0], image.shape[1], image.shape[2], width_cap / height_cap,
                                        view_distance)
            glBindTexture(GL_TEXTURE_2D, texture)
            image_data = image[:, count - countdown + 1, :]
            image_data = image_data.flatten().astype(np.float32)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, image.shape[2], image.shape[0], 0, GL_RED, GL_FLOAT, image_data)

            glUseProgram(slice_shader)
            glActiveTexture(GL_TEXTURE0)
            glBindVertexArray(VAOS)
            glBindTexture(GL_TEXTURE_2D, texture)
            glUniformMatrix4fv(view_loc_slice, 1, GL_FALSE, view)
            glUniformMatrix4fv(model_loc_slice, 1, GL_FALSE, model)
            glUniformMatrix4fv(proj_loc_slice, 1, GL_FALSE, projection)
            glUniform1f(max_height_loc_slice, count - countdown)
            glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
            # glBindTexture(GL_TEXTURE_2D, 0)

            glUseProgram(voxel_shader)
            glUniformMatrix4fv(model_loc_voxel, 1, GL_FALSE, model)
            glUniformMatrix4fv(view_loc_voxel, 1, GL_FALSE, view)
            glUniformMatrix4fv(proj_loc_voxel, 1, GL_FALSE, projection)
            glUniform1f(max_height_loc_voxel, count)

            # draw each label
            for i in range(len(labels)):
                glBindVertexArray(array_vertex_array_object[i])
                glUniform4f(label_color_loc_voxel,
                            labels_colors[i][0],
                            labels_colors[i][1],
                            labels_colors[i][2],
                            labels_colors[i][3])
                glDrawArrays(GL_POINTS, 0, array_nb_voxels[i])

            if only_image:
                glUseProgram(texbox_shader)
                glUniformMatrix4fv(model_loc_texbox, 1, GL_FALSE, model)
                glUniformMatrix4fv(view_loc_texbox, 1, GL_FALSE, view)
                glUniformMatrix4fv(proj_loc_texbox, 1, GL_FALSE, projection)
                # glUniform1f(max_height_loc_texbox,  count - countdown)
                glUniform1f(max_height_loc_texbox, count)
                glBindVertexArray(VAO_texbox0)
                glBindTexture(GL_TEXTURE_2D, texture0)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
                glBindVertexArray(VAO_texbox1)
                glBindTexture(GL_TEXTURE_2D, texture1)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
                glBindVertexArray(VAO_texbox2)
                glBindTexture(GL_TEXTURE_2D, texture2)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
                glBindVertexArray(VAO_texbox3)
                glBindTexture(GL_TEXTURE_2D, texture3)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)

            # capture system
            if capture is not None:
                x_cap, y_cap, width_cap, height_cap = glGetDoublev(GL_VIEWPORT)
                width_cap, height_cap = int(width_cap), int(height_cap)
                glPixelStorei(GL_PACK_ALIGNMENT, 1)
                data = glReadPixels(x_cap, y_cap, width_cap, height_cap, GL_RGB, GL_UNSIGNED_BYTE)

                image_cap = Image.frombytes("RGB", (width_cap, height_cap), data)
                image_cap = image_cap.transpose(Image.FLIP_TOP_BOTTOM)

                if capture == 0:
                    # save each frame as a png
                    filename = output + "/" + str(frame_n).zfill(8) + ".png"
                    image_cap.save(filename, "PNG")
                elif capture > frame_n:
                    # save frame in memory
                    capture_img.append(image_cap)
                elif capture == frame_n:
                    # convert saved frame in video
                    capture_img.append(image_cap)
                    fourcc = cv2.VideoWriter_fourcc(*'avc1')
                    video = cv2.VideoWriter(output, fourcc, video_fps, (width_cap, height_cap))
                    for tmp in capture_img:
                        video.write(cv2.cvtColor(np.array(tmp), cv2.COLOR_RGB2BGR))
                    video.release()
                    capture = None

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


def place_camera(imageX, imageY, imageZ, view_distance):
    # max_dim
    height = 0.65
    diag = np.sqrt(imageX ** 2 + imageY ** 2 + imageZ ** 2)
    # distance = 2 * (imageX if imageX > imageZ else imageZ)
    camera_pos = Vector3([0.0, imageY * height, view_distance * -diag])
    camera_target = Vector3([0.0, 0.0, 0.0])
    camera_front = vector.normalise(camera_target - camera_pos)

    return matrix44.create_look_at(camera_pos, camera_pos + camera_front, Vector3([0.0, 1.0, 0.0]))


def get_projection(imageX, imageY, imageZ, ratio, view_distance):
    max_dist = np.sqrt(imageX ** 2 + imageY ** 2 + imageZ ** 2)
    return matrix44.create_perspective_projection_matrix(45.0, ratio, 10, max_dist * 2 * view_distance)


def get_vertices(image_shape):
    slice_vertices = np.array([
        0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, image_shape[2], 1.0, 0.0,
        image_shape[0], 0.0, image_shape[2], 1.0, 1.0,
        image_shape[0], 0.0, 0.0, 0.0, 1.0
    ], dtype=np.float32)

    texbox0_vertices = np.array([
        0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, image_shape[2], 1.0, 0.0,
        0.0, image_shape[1], image_shape[2], 1.0, 1.0,
        0.0, image_shape[1], 0.0, 0.0, 1.0
    ], dtype=np.float32)

    texbox1_vertices = np.array([
        0.0, 0.0, image_shape[2], 0.0, 0.0,
        image_shape[0], 0.0, image_shape[2], 1.0, 0.0,
        image_shape[0], image_shape[1], image_shape[2], 1.0, 1.0,
        0.0, image_shape[1], image_shape[2], 0.0, 1.0
    ], dtype=np.float32)

    texbox2_vertices = np.array([
        image_shape[0], 0.0, image_shape[2], 0.0, 0.0,
        image_shape[0], 0.0, 0.0, 1.0, 0.0,
        image_shape[0], image_shape[1], 0.0, 1.0, 1.0,
        image_shape[0], image_shape[1], image_shape[2], 0.0, 1.0
    ], dtype=np.float32)

    texbox3_vertices = np.array([
        image_shape[0], 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0, 0.0,
        0.0, image_shape[1], 0.0, 1.0, 1.0,
        image_shape[0], image_shape[1], 0.0, 0.0, 1.0
    ], dtype=np.float32)

    return (slice_vertices,
            texbox0_vertices,
            texbox1_vertices,
            texbox2_vertices,
            texbox3_vertices)
