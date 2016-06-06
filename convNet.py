import random
from collections import deque
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

TRAINING_BATCH_SIZE = 100


def weight_variable(shape, name):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial, name=name)


def bias_variable(shape, name):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial, name=name)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool(x):
    return tf.nn.max_pool(x, ksize=[1, POOLING_SIZE, POOLING_SIZE, 1], strides=[1, POOLING_SIZE, POOLING_SIZE, 1],
                          padding='SAME')


def _create_network():
    sess = tf.Session()
    input_layer = tf.placeholder(tf.float32, shape=[None, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS])
    # Layer 1
    W_conv1 = weight_variable([LAYER1_PATCH_SIZE, LAYER1_PATCH_SIZE, DATA_CHANNELS, LAYER1_FEATURES], name = "W_conv1")
    b_conv1 = bias_variable([LAYER1_FEATURES], name = "b_conv1")
    h_conv1 = tf.nn.relu(conv2d(input_layer, W_conv1) + b_conv1)
    h_pool1 = max_pool(h_conv1)
    # Layer 2
    W_conv2 = weight_variable([LAYER1_PATCH_SIZE, LAYER2_PATCH_SIZE, LAYER1_FEATURES, LAYER2_FEATURES], name = "W_conv2")
    b_conv2 = bias_variable([LAYER2_FEATURES], name = "b_conv2")
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool(h_conv2)
    # Layer 3
    W_fc1 = weight_variable([FINAL_VECTOR_SIZE, FINAL_FEATURES], name = "W_fc1")
    b_fc1 = bias_variable([FINAL_FEATURES], name = "b_fc1")
    h_pool2_flat = tf.reshape(h_pool2, [-1, FINAL_VECTOR_SIZE])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    # Final Layer
    W_fc2 = weight_variable([FINAL_FEATURES, N_DIRECTIONS], name = "W_fc2")
    b_fc2 = bias_variable([N_DIRECTIONS], name = "b_fc2")
    # Output Layer
    output_layer = tf.nn.softmax(tf.matmul(h_fc1, W_fc2) + b_fc2)
    return input_layer, h_fc1, output_layer


class ConvNet:
    OBS_LAST_STATE_INDEX, OBS_ACTION_INDEX, OBS_REWARD_INDEX, OBS_CURRENT_STATE_INDEX, OBS_TERMINAL_INDEX = range(5)
    FUTURE_REWARD_DISCOUNT = 0.99

    def __init__(self):
        self.step_counter = 0
        self._action = tf.placeholder("float", [None, N_DIRECTIONS])
        self._target = tf.placeholder("float", [None])

        self._previous_observations = deque()
        self._session = tf.Session()
        self._input_layer, self._map_layer, self._output_layer = _create_network()

        readout_action = tf.reduce_sum(tf.mul(self._output_layer, self._action), reduction_indices=1)
        cost = tf.reduce_mean(tf.square(self._target - readout_action))
        self._train_operation = tf.train.AdamOptimizer(1e-6).minimize(cost)

        self._session.run(tf.initialize_all_variables())
        self.saver = tf.train.Saver()

    def _train(self):
        pass

    def calculateDecisions(self, state):
        # self.sess.run(tf.initialize_all_variables())
        # dims = state.get_shape();

        dir_weights = self._session.run(self._output_layer, feed_dict={self._input_layer: [state]})
        # self._input_layer = tf.Variable(tf.random_normal(shape=[1, MAX_MAP_SIZE, MAX_MAP_SIZE, DATA_CHANNELS]))
        # print(h_pool2.get_shape())
        # self.sess.run(tf.initialize_all_variables())
        # (mapFeatures, dir_weights) = self.session.run((self.out))
        return dir_weights[0]

    def trainNetwork(self, transitions):
        if len(transitions) > TRAINING_BATCH_SIZE:
            mini_batch = random.sample(transitions, TRAINING_BATCH_SIZE)

            previous_states = [d[self.OBS_LAST_STATE_INDEX] for d in mini_batch]
            actions = [d[self.OBS_ACTION_INDEX] for d in mini_batch]
            rewards = [d[self.OBS_REWARD_INDEX] for d in mini_batch]
            current_states = [d[self.OBS_CURRENT_STATE_INDEX] for d in mini_batch]

            agents_expected_reward = []
            # this gives us the agents expected reward for each action we might
            agents_reward_per_action = self._output_layer.eval(feed_dict={self._input_layer: current_states}, session=self._session)
            for i in range(len(mini_batch)):
                # if mini_batch[i][self.OBS_TERMINAL_INDEX]:
                #     # this was a terminal frame so need so scale future reward...
                #     agents_expected_reward.append(rewards[i])
                # else:
                expected_reward = rewards[i] + self.FUTURE_REWARD_DISCOUNT * numpy.max(agents_reward_per_action[i])
                agents_expected_reward.append(expected_reward)

            # learn that these actions in these states lead to this reward
            self._train_operation.run(feed_dict={
                self._input_layer: previous_states,
                self._action: actions,
                self._target: agents_expected_reward},
                session=self._session)

            print('Trained')
            self.saver.save(self._session, "convNet/model.ckpt")
            self.step_counter += 1
        # L = pow(r + GAMMA*Q_table.max() + Qtable.max())/2
        # error_vector = numpy.zeros(N_DIRECTIONS)
        # error_vector[actionIndex] = L
        # tf.train.AdamOptimizer(1e-4).minimize()

if __name__ == "__main__":
    net = ConvNet()
    forma = "%0.4f"
    for i in range(50):
        start_time = time.time()
        state = numpy.random.random_integers(0, 5, (MAX_MAP_SIZE, MAX_MAP_SIZE, 2))
        # print(state.shape())
        w = net.calculateDecisions(state)
        # print(w)
        # print(w.argmax(1))
        print(forma % w[0], forma % w[1], forma % w[2], forma % w[3], forma % w[4])
        print("%d --- %0.4f seconds --- %s" % (i, time.time() - start_time, w.argmax(0)))
        time.sleep(0.25)

