import tensorflow as tf

MAX_MAP_SIZE = 28
IMAGE_SIZE = MAX_MAP_SIZE * MAX_MAP_SIZE
DATA_CHANNELS = 2
N_DIRECTIONS = 5
POOLING_SIZE = 2

LAYER1_FEATURES = 32
LAYER1_PATCH_SIZE = 4

LAYER2_FEATURES = 64
LAYER2_PATCH_SIZE = 4

FINAL_VECTOR_SIZE = pow(MAX_MAP_SIZE / pow(POOLING_SIZE, 2), 2) * LAYER2_FEATURES
FINAL_FEATURES = 1024


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool(x):
    return tf.nn.max_pool(x, ksize=[1, POOLING_SIZE, POOLING_SIZE, 1], strides=[1, POOLING_SIZE, POOLING_SIZE, 1],
                          padding='SAME')


class ConvNet:
    @staticmethod
    def calculateDecisions(inputData):
        hello = tf.constant('Hello let\'s start!')
        sess = tf.Session()
        print(sess.run(hello))

        # x = tf.placeholder(tf.float32, shape=[None, IMAGE_SIZE])
        inputData = tf.Variable(tf.random_normal(shape=[1, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS]))
        # y_ = tf.placeholder(tf.float32, shape=[None, N_DIRECTIONS])
        # expectedOut = tf.Variable(tf.random_normal(shape=[]))

        # Weights
        W = tf.Variable(tf.zeros([IMAGE_SIZE, N_DIRECTIONS]))
        # Network Biases
        b = tf.Variable(tf.zeros([N_DIRECTIONS]))

        # Layer 1
        W_conv1 = weight_variable([LAYER1_PATCH_SIZE, LAYER1_PATCH_SIZE, DATA_CHANNELS, LAYER1_FEATURES])
        b_conv1 = bias_variable([LAYER1_FEATURES])

        h_conv1 = tf.nn.relu(conv2d(inputData, W_conv1) + b_conv1)
        h_pool1 = max_pool(h_conv1)

        # Layer 2
        W_conv2 = weight_variable([LAYER1_PATCH_SIZE, LAYER2_PATCH_SIZE, LAYER1_FEATURES, LAYER2_FEATURES])
        b_conv2 = bias_variable([LAYER2_FEATURES])

        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = max_pool(h_conv2)

        # Layer 3
        W_fc1 = weight_variable([FINAL_VECTOR_SIZE, FINAL_FEATURES])
        b_fc1 = bias_variable([FINAL_FEATURES])

        h_pool2_flat = tf.reshape(h_pool2, [-1, FINAL_VECTOR_SIZE])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

        # Final Layer
        W_fc2 = weight_variable([FINAL_FEATURES, N_DIRECTIONS])
        b_fc2 = bias_variable([N_DIRECTIONS])

        # print(h_fc1.get_shape())
        # print(W_fc2.get_shape())
        # print(b_fc2.get_shape())

        y_conv = tf.nn.softmax(tf.matmul(h_fc1, W_fc2) + b_fc2)

        sess.run(tf.initialize_all_variables())
        # print(h_pool2.get_shape())
        dirWeights = sess.run(y_conv)
        return dirWeights

if __name__ == "__main__":
    w = ConvNet.calculateDecisions("")
    print(w)
    print(w.argmax(1))
