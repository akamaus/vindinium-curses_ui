import tensorflow as tf
import numpy
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

GAMMA = 0.6


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


def _create_network():
    sess = tf.Session()
    input_layer = tf.placeholder(tf.float32, shape=[1, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS])
    # Layer 1
    W_conv1 = weight_variable([LAYER1_PATCH_SIZE, LAYER1_PATCH_SIZE, DATA_CHANNELS, LAYER1_FEATURES])
    b_conv1 = bias_variable([LAYER1_FEATURES])
    h_conv1 = tf.nn.relu(conv2d(input_layer, W_conv1) + b_conv1)
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
    # Output Layer
    output_layer = tf.nn.softmax(tf.matmul(h_fc1, W_fc2) + b_fc2)
    sess.run(tf.initialize_all_variables())
    return input_layer, h_fc1, output_layer


class ConvNet:

    def __init__(self):
        self._action = tf.placeholder("float", [None, N_DIRECTIONS])
        self._target = tf.placeholder("float", [None])

        self._previous_observations = []
        self._session = tf.Session()
        self._input_layer, self._map_layer, self._output_layer = _create_network()

        readout_action = tf.reduce_sum(tf.mul(self._output_layer, self._action), reduction_indices=1)

        cost = tf.reduce_mean(tf.square(self._target - readout_action))
        self._train_operation = tf.train.AdamOptimizer(1e-6).minimize(cost)

        self._session.run(tf.initialize_all_variables())

    def _train(self):
        pass

    def calculateDecisions(self, state):
        # self.sess.run(tf.initialize_all_variables())
        # dims = state.get_shape();

        dir_weights = self._session.run(self._output_layer, feed_dict = {self._input_layer: [state]})
        # self._input_layer = tf.Variable(tf.random_normal(shape=[1, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS]))
        # print(h_pool2.get_shape())
        # self.sess.run(tf.initialize_all_variables())
        # (mapFeatures, dir_weights) = self.session.run((self.out))
        return dir_weights[0]

    # def trainNetwork(self):
    #     L = pow(r + GAMMA*Q_table.max() + Qtable.max())/2
    #     error_vector = numpy.zeros(N_DIRECTIONS)
    #     error_vector[actionIndex] = L
    #     tf.train.AdamOptimizer(1e-4).minimize()

if __name__ == "__main__":
    net = ConvNet()
    for i in range(50):
        start_time = time.time()
        state = numpy.random.random_integers(0, 5, (MAX_MAP_SIZE, MAX_MAP_SIZE, 2))
        # print(state.shape())
        w = net.calculateDecisions(state)
        # print(w)
        # print(w.argmax(1))
        # print(w[0], w[1], w[2], w[3], w[4])
        print("%d --- %s seconds --- %s" % (i, time.time() - start_time, w.argmax(0)))
        time.sleep(0.25)

