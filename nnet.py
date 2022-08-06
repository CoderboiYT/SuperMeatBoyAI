import random
import numpy as np
import scipy.special

from settings import MUTATION_WEIGHT_MODIFY_CHANCE, MUTATION_ARRAY_MIX_PERC, train, lvl, load_weights


class NNet:
    def __init__(self, num_input, num_hidden, num_output):
        self.num_input = num_input
        self.num_hidden_1 = num_hidden
        self.num_hidden_2 = num_hidden
        self.num_output = num_output
        if train and not load_weights:
            self.weight_input_hidden = np.random.uniform(
                -100, 100, size=(self.num_hidden_1, self.num_input))
            self.weight_hidden_hidden = np.random.uniform(
                -100, 100, size=(self.num_hidden_2, self.num_hidden_1))
            self.weight_hidden_output = np.random.uniform(
                -100, 100, size=(self.num_output, self.num_hidden_2))
        else:
            self.load_weights()
        self.activation_function = lambda x: scipy.special.expit(x)

    def get_outputs(self, inputs_list):
        inputs = np.array(inputs_list, ndmin=2).T
        x = np.dot(self.weight_input_hidden, inputs)
        x = self.activation_function(x)
        x = np.dot(self.weight_hidden_hidden, x)
        x = self.activation_function(x)
        x = np.dot(self.weight_hidden_output, x)
        final_outputs = self.activation_function(x)
        return final_outputs

    def save_weights(self):
        np.savetxt(f'./weights/input_hidden_{lvl}.txt',
                   self.weight_input_hidden, fmt='%5.4g', delimiter=',')
        np.savetxt(f'./weights/hidden_hidden_{lvl}.txt',
                   self.weight_hidden_hidden, fmt='%5.4g', delimiter=',')
        np.savetxt(f'./weights/hidden_output_{lvl}.txt',
                   self.weight_hidden_output, fmt='%5.4g', delimiter=',')

    def load_weights(self):
        self.weight_input_hidden = np.loadtxt(
            f'./weights/input_hidden_{lvl}.txt', dtype=float, delimiter=',')
        self.weight_hidden_hidden = np.loadtxt(
            f'./weights/hidden_hidden_{lvl}.txt', dtype=float, delimiter=',')
        self.weight_hidden_output = np.loadtxt(
            f'./weights/hidden_output_{lvl}.txt', dtype=float, delimiter=',')

    def get_final_value(self, inputs_list):
        outputs = self.get_outputs(inputs_list)
        return outputs.flatten()

    def modify_weights(self):
        NNet.modify_array(self.weight_input_hidden)
        NNet.modify_array(self.weight_hidden_hidden)
        NNet.modify_array(self.weight_hidden_output)

    def create_mixed_weights(self, net1, net2):
        self.weight_input_hidden = NNet.get_mix_from_arrays(
            net1.weight_input_hidden, net2.weight_input_hidden)
        self.weight_hidden_hidden = NNet.get_mix_from_arrays(
            net1.weight_hidden_hidden, net2.weight_hidden_hidden)
        self.weight_hidden_output = NNet.get_mix_from_arrays(
            net1.weight_hidden_output, net2.weight_hidden_output)

    def modify_array(a):
        for x in np.nditer(a, op_flags=['readwrite']):
            if random.random() < MUTATION_WEIGHT_MODIFY_CHANCE:
                x[...] = np.random.random_sample() - 0.5

    def get_mix_from_arrays(ar1, ar2):
        total_entries = ar1.size
        num_rows = ar1.shape[0]
        num_cols = ar1.shape[1]

        num_to_take = total_entries - \
            int(total_entries * MUTATION_ARRAY_MIX_PERC)
        idx = np.random.choice(np.arange(total_entries),
                               num_to_take, replace=False)

        res = np.random.rand(num_rows, num_cols)

        for row in range(0, num_rows):
            for col in range(0, num_cols):
                index = row * num_cols + col
                if index in idx:
                    res[row][col] = ar1[row][col]
                else:
                    res[row][col] = ar2[row][col]

        return res
