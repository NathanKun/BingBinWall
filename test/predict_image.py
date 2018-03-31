import numpy as np

import tensorflow as tf

TEST_IMAGE_PATH = './glass17.jpg'
FROZEN_MODEL_PATH = './graph.pb'
INPUT_SIZE = 224
INDEX_2_LABEL = {
    0: 'cardboard',
    1: 'plastic',
    2: 'paper',
    3: 'glass',
    4: 'metal'
}


def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
                                input_mean=0, input_std=255):
    input_name = "file_reader"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels=3,
                                           name='png_reader')
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                      name='gif_reader'))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    else:
        image_reader = tf.image.decode_jpeg(file_reader, channels=3,
                                            name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result


def load_frozen_graph(frozen_model):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(frozen_model, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    return detection_graph


def predict(image_path, frozen_model_path, label_mapping, input_name="input:0", output_name="final_result:0"):
    """
    Predict image category.

    :param image_path: str
    :param frozen_model_path: str
    :param label_mapping: dict
    :param input_name: str
    :param output_name: str

    :return: category and probability
    :rtype: (str, float)
    """
    graph = load_frozen_graph(frozen_model_path)
    image_tensor = read_tensor_from_image_file(image_path,
                                               input_height=INPUT_SIZE,
                                               input_width=INPUT_SIZE)
    input_tensor = graph.get_tensor_by_name(input_name)
    output_tensor = graph.get_tensor_by_name(output_name)
    with tf.Session(graph=graph) as sess:
        results = sess.run(output_tensor,
                           {input_tensor: image_tensor})
    results = np.squeeze(results)
    top_index = results.argsort()[-1]
    label = label_mapping[top_index]
    return label, results[top_index]


# print(predict(TEST_IMAGE_PATH, FROZEN_MODEL_PATH, INDEX_2_LABEL))  # expected output: ('cardboard', 0.8138799)
