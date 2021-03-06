from .Base import NetworkBase
from ..utils.activations import *
from ..utils.initializers import *


class Network(NetworkBase):
    def __init__(self, sizes=[100, 100], activation="relu", dropout_rate=0.0):
        """
        :param sizes: list of layers
        :param activations: activation_functions
        """
        self.sizes = sizes
        self.num_layers = len(sizes)
        self.weights = [np.random.randn(back_layer, forward_layer) * np.sqrt(2.0 / forward_layer)
                        for forward_layer, back_layer in zip(sizes[:-1], sizes[1:])]
        self.biases = [np.random.randn(back_layer, 1) for back_layer in sizes[1:]]
        self.dropout_rate = dropout_rate

    def predict(self, a):
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            a = self.activation(np.dot(w, a) + b)
            a *= (1.0 - self.dropout_rate)  ######### test dropout
        a = np.dot(self.weights[-1], a) + self.biases[-1]
        return a

    def backprop(self, x, y):
        gradient_w = [np.zeros(w.shape) for w in self.weights]
        gradient_b = [np.zeros(b.shape) for b in self.biases]

        # forward pass #
        a = x
        a_hold = [x]
        z_hold = []
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            z = np.dot(w, a) + b

            self.mask = np.random.rand(*z.shape) > self.dropout_rate
            z *= self.mask
            #    z /= (1 - self.dropout_rate)

            a = self.activation(z)
            z_hold.append(z)
            a_hold.append(a)
        final_layer = np.dot(self.weights[-1], a) + self.biases[-1]
        z_hold.append(final_layer)
        a_hold.append(self.last_layer.forward(final_layer))

        # backward pass#
        delta = self.last_layer.derivative_with_cross_entropy(a_hold[-1], y)
        gradient_w[-1] = np.dot(delta, a_hold[-2].T)
        gradient_b[-1] = delta

        for l in range(2, self.num_layers):
            delta = np.dot(self.weights[-l + 1].T, delta) * self.activation.derivative(z_hold[-l])
            gradient_w[-l] = np.dot(delta, a_hold[-l - 1].T)
            gradient_b[-l] = delta

        return gradient_w, gradient_b



class Network_mini_batch(NetworkBase):
    def __init__(self, sizes=[100, 100], activation="relu", last_layer="softmax",
                 seed=42, dropout_rate=0.0, **kwargs):
        """
        :param sizes: list of neural network layer sizes
        :param activation: activation functions
        :param last_layer: output layer/function
        """
        super(Network_mini_batch, self).__init__(sizes, activation, last_layer, **kwargs)
        self.seed = seed
        self.__init_params(mode=kwargs.get("weight_initializer", "xavier"))
        if 0.0 <= dropout_rate <= 1.0:
            self.dropout_rate = dropout_rate
            self.train = True
        else:
            raise ValueError("dropout rate must be in [0.0, 1.0], find value: {}".format(dropout_rate))

    def __init_params(self, mode="xavier"):
        np.random.seed(self.seed)
        if mode == "normal":
            self.weights = [truncated_normal(mean=0.0, scale=0.05, shape=[forward_layer, back_layer])  # scale = 0.01 / 0.1
                            for forward_layer, back_layer in zip(self.sizes[:-1], self.sizes[1:])]
        elif mode == "xavier":
        #    self.weights = [truncated_normal(0.0, 0.01, [forward_layer, back_layer]) * np.sqrt(1.0 / forward_layer)
        #                    for forward_layer, back_layer in zip(self.sizes[:-1], self.sizes[1:])]
            self.weights = [variance_scaling(scala=1.0, fan_in=forward_layer, fan_out=back_layer, mode="fan_average")
                            for forward_layer, back_layer in zip(self.sizes[:-1], self.sizes[1:])]
        elif mode == "he": # np.random.randn
            self.weights = [variance_scaling(scala=2.0, fan_in=forward_layer, fan_out=back_layer, mode="fan_in")
                            for forward_layer, back_layer in zip(self.sizes[:-1], self.sizes[1:])]
        else:
            raise ValueError('Unknown weight initializer mode: {}.'.format(mode))

        self.biases = [np.random.randn(layer) for layer in self.sizes[1:]]

    def predict(self, a):
    #    for w, b in zip(self.weights[:-1], self.biases[:-1]):
    #        a = self.activation(np.dot(a, w) + b)
        #    a *= (1.0 - self.dropout_rate)

        for i, (w, b) in enumerate(zip(self.weights[:-1], self.biases[:-1])):
            a = self.activation(np.dot(a, w) + b)
            if i == 0:
                a *= (1.0 - self.dropout_rate)
            if i > 0:
                a *= (1.0 - self.dropout_rate)

        #    a *= (1.0 - self.dropout_rate)
        a = np.dot(a, self.weights[-1]) + self.biases[-1]
        return a

    def backprop(self, x, y):
        gradient_w = [np.zeros(w.shape) for w in self.weights]
        gradient_b = [np.zeros(b.shape) for b in self.biases]

        a = x
        a_hold = [x]
        z_hold = []
        for i, (w, b) in enumerate(zip(self.weights[:-1], self.biases[:-1])):
            z = np.dot(a, w) + b  # batch  z = a * w + b
        #    if self.dropout_rate > 0.0:
        #        mask = np.random.rand(*z.shape) > self.dropout_rate
        #        z *= mask

            if self.dropout_rate > 0.0 and i == 0:
                mask = np.random.rand(*z.shape) > self.dropout_rate
                z *= mask

            if self.dropout_rate > 0.0 and i > 0:
                mask = np.random.rand(*z.shape) > self.dropout_rate
                z *= mask
            #    z /= (1 - self.dropout_rate)
            a = self.activation(z)
            z_hold.append(z)
            a_hold.append(a)
        final_layer = np.dot(a, self.weights[-1]) + self.biases[-1]
        z_hold.append(final_layer)
        a_hold.append(self.last_layer.forward(final_layer))

        delta = self.last_layer.derivative_with_cross_entropy(a_hold[-1], y)
        gradient_w[-1] = np.dot(a_hold[-2].T, delta)
        gradient_b[-1] = np.sum(delta, axis=0)

        for l in range(2, self.num_layers):
            delta = np.dot(delta, self.weights[-l + 1].T) * self.activation.derivative(z_hold[-l])
            gradient_w[-l] = np.dot(a_hold[-l - 1].T, delta)
            gradient_b[-l] = np.sum(delta, axis=0)

        return gradient_w, gradient_b

    @property
    def params(self):
        return self.weights, self.biases

