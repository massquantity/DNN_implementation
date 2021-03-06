import time
from DNN_implementation.data import cifar_data, mnist_2
from DNN_implementation.model import Network, Network_mini_batch
from DNN_implementation.train import train_DNN_minibatch
from DNN_implementation import Sgd, Momentum, NesterovMomentum, Adam, Adagrad
from DNN_implementation import Sigmoid, ReLU


if __name__ == "__main__":
    print("------------------", "test benchmark", "----------------------")
    '''
    (X_train, y_train), (X_test, y_test) = cifar_data.load_data(normalize=False, standard=True)  # standardscale
    dnn = Network_mini_batch(sizes=[3072, 1000, 500, 200, 10], activation="relu", alpha=0.01, dropout_rate=0.3, # alpha=0.1
                             weight_initializer="xavier")
#    optimizer = Sgd(lr=1.0, batch_size=256)
#    optimizer = Momentum(lr=3e-3, momentum=0.9, batch_size=256)
    optimizer = Adam(lr=1e-4, batch_size=256)
    start_time = time.time()
    train_DNN_minibatch(X_train, y_train, 150, optimizer, 256, dnn, X_test, y_test,
                        early_stopping=True, patience=20, metrics="accuracy", evaluate=True,
                        lr_decay_rate=0.99, lr_decay_mode="exponential", batch_mode="normal")  #
    print("training time: {:.2f}".format(time.time() - start_time))
    print()
    '''

    (X_train, y_train), (X_test, y_test) = mnist_2.load_data()
    dnn = Network_mini_batch(sizes=[784, 300, 100, 10], activation="relu", alpha=0.1, dropout_rate=0.3,  # dropout alpha
                             weight_initializer="he")
    optimizer = Adagrad(lr=1e-1, batch_size=256)
#    optimizer = Adam(lr=1e-4, batch_size=256)  # 1e-3
#    optimizer = Sgd(lr=1e-2, batch_size=256)
#    optimizer = Momentum(lr=1e-3, momentum=0.9, batch_size=256)
    start_time = time.time()
    train_DNN_minibatch(X_train, y_train, 500, optimizer, 256, dnn, X_test, y_test,
                        early_stopping=True, patience=20, metrics="accuracy", evaluate=True,
                        )  # lr_decay_rate=0.99, lr_decay_mode="normal", batch_mode="balance"
    print("training time: {:.2f}".format(time.time() - start_time))
    print()





