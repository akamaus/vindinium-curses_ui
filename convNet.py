import tensorflow as tf
import time

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

    def __init__(self):
        self.sess = tf.Session()
        # x = tf.placeholder(tf.float32, shape=[None, IMAGE_SIZE])
        self.inputData = tf.Variable(tf.random_normal(shape=[1, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS]))
        # y_ = tf.placeholder(tf.float32, shape=[None, N_DIRECTIONS])
        # expectedOut = tf.Variable(tf.random_normal(shape=[]))

        # Weights
        self.W = tf.Variable(tf.zeros([IMAGE_SIZE, N_DIRECTIONS]))
        # Network Biases
        self.b = tf.Variable(tf.zeros([N_DIRECTIONS]))

        # Layer 1
        self.W_conv1 = weight_variable([LAYER1_PATCH_SIZE, LAYER1_PATCH_SIZE, DATA_CHANNELS, LAYER1_FEATURES])
        self.b_conv1 = bias_variable([LAYER1_FEATURES])

        self.h_conv1 = tf.nn.relu(conv2d(self.inputData, self.W_conv1) + self.b_conv1)
        self.h_pool1 = max_pool(self.h_conv1)

        # Layer 2
        self.W_conv2 = weight_variable([LAYER1_PATCH_SIZE, LAYER2_PATCH_SIZE, LAYER1_FEATURES, LAYER2_FEATURES])
        self.b_conv2 = bias_variable([LAYER2_FEATURES])

        self.h_conv2 = tf.nn.relu(conv2d(self.h_pool1, self.W_conv2) + self.b_conv2)
        self.h_pool2 = max_pool(self.h_conv2)

        # Layer 3
        self.W_fc1 = weight_variable([FINAL_VECTOR_SIZE, FINAL_FEATURES])
        self.b_fc1 = bias_variable([FINAL_FEATURES])

        self.h_pool2_flat = tf.reshape(self.h_pool2, [-1, FINAL_VECTOR_SIZE])
        self.h_fc1 = tf.nn.relu(tf.matmul(self.h_pool2_flat, self.W_fc1) + self.b_fc1)

        # Final Layer
        self.W_fc2 = weight_variable([FINAL_FEATURES, N_DIRECTIONS])
        self.b_fc2 = bias_variable([N_DIRECTIONS])

        # print(h_fc1.get_shape())
        # print(W_fc2.get_shape())
        # print(b_fc2.get_shape())

        self.y_conv = tf.nn.softmax(tf.matmul(self.h_fc1, self.W_fc2) + self.b_fc2)
        self.sess.run(tf.initialize_all_variables())

    def calculateDecisions(self, input):
        # self.sess.run(tf.initialize_all_variables())
        self.inputData = tf.Variable(tf.random_normal(shape=[1, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS]))
        # print(h_pool2.get_shape())
        self.sess.run(tf.initialize_all_variables())
        dirWeights = self.sess.run(self.y_conv)
        return dirWeights

if __name__ == "__main__":
    net = ConvNet()
    for i in range(50):
        start_time = time.time()
        w = net.calculateDecisions("")
        # print(w)
        # print(w.argmax(1))
        print("%d --- %s seconds --- %s" % (i, time.time() - start_time, w.argmax(1)[0]))
        time.sleep(0.25)

