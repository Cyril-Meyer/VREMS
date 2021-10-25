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
    voxel_shader = shader.compile_shader_geometry("shaders/voxel_shader.vs",
                                                  "shaders/voxel_shader.fs",
                                                  "shaders/voxel_shader.gs")
    slice_shader = shader.compile_shader("shaders/slice_shader.vs",
                                         "shaders/slice_shader.fs")
    texbox_shader = shader.compile_shader("shaders/texbox_shader.vs",
                                          "shaders/texbox_shader.fs")

    # slice plane
    slice_vertices, texbox0_vertices, texbox1_vertices, texbox2_vertices, texbox3_vertices = get_vertices(image.shape)

    slice_indices = [0, 1, 2,
                     0, 2, 3]
    slice_indices = np.array(slice_indices, dtype=np.uint32)

    # geometry data
    vaos, vbos, ebos, position_s, tex_coord = create_object_buffer(slice_vertices, slice_indices, slice_shader)

    if only_image:
        vao_texbox0, vbo_texbox0, ebo_texbox0, _, _ = create_object_buffer(texbox0_vertices, slice_indices, texbox_shader)
        vao_texbox1, vbo_texbox1, ebo_texbox1, _, _ = create_object_buffer(texbox1_vertices, slice_indices, texbox_shader)
        vao_texbox2, vbo_texbox2, ebo_texbox2, _, _ = create_object_buffer(texbox2_vertices, slice_indices, texbox_shader)
        vao_texbox3, vbo_texbox3, ebo_texbox3, _, _ = create_object_buffer(texbox3_vertices, slice_indices, texbox_shader)

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
        texture0 = create_slice_texture(image[0, :, :], image.shape[2], image.shape[1])
        texture1 = create_slice_texture(np.flip(np.rot90(image[:, :, -1]), 0), image.shape[0], image.shape[1])
        texture2 = create_slice_texture(np.flip(image[-1, :, :], 1), image.shape[2], image.shape[1])
        texture3 = create_slice_texture(np.flip(np.flip(np.rot90(image[:, :, 0]), 0), 1), image.shape[0], image.shape[1])


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
            glBindVertexArray(vaos)
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
                glBindVertexArray(vao_texbox0)
                glBindTexture(GL_TEXTURE_2D, texture0)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
                glBindVertexArray(vao_texbox1)
                glBindTexture(GL_TEXTURE_2D, texture1)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
                glBindVertexArray(vao_texbox2)
                glBindTexture(GL_TEXTURE_2D, texture2)
                glDrawElements(GL_TRIANGLES, len(slice_indices), GL_UNSIGNED_INT, None)
                glBindVertexArray(vao_texbox3)
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
                    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
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


def place_camera(image_x, image_y, image_z, view_distance):
    # max_dim
    height = 0.65
    diag = np.sqrt(image_x ** 2 + image_y ** 2 + image_z ** 2)
    # distance = 2 * (imageX if imageX > imageZ else imageZ)
    camera_pos = Vector3([0.0, image_y * height, view_distance * -diag])
    camera_target = Vector3([0.0, 0.0, 0.0])
    camera_front = vector.normalise(camera_target - camera_pos)

    return matrix44.create_look_at(camera_pos, camera_pos + camera_front, Vector3([0.0, 1.0, 0.0]))


def get_projection(image_x, image_y, image_z, ratio, view_distance):
    max_dist = np.sqrt(image_x ** 2 + image_y ** 2 + image_z ** 2)
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


def create_object_buffer(vertices, indices, shader=None):
    vaos = glGenVertexArrays(1)
    glBindVertexArray(vaos)

    vbos = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbos)
    glBufferData(GL_ARRAY_BUFFER, vertices.itemsize * len(vertices), vertices, GL_STATIC_DRAW)

    ebos = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebos)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)

    position_s = glGetAttribLocation(shader, "position")
    glVertexAttribPointer(position_s, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position_s)

    tex_coord = glGetAttribLocation(shader, "inTexCoord")
    glVertexAttribPointer(tex_coord, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(12))
    glEnableVertexAttribArray(tex_coord)

    return vaos, vbos, ebos, position_s, tex_coord


def create_slice_texture(image_data, shape0, shape1):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    image_data = image_data.flatten().astype(np.float32)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, shape0, shape1, 0, GL_RED, GL_FLOAT, image_data)

    return texture
