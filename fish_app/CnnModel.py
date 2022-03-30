import keras, os, numpy as np
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D, Flatten
from keras.optimizers import Adam
from keras.layers import BatchNormalization, Dropout
from flask import current_app
from keras.preprocessing.image import load_img, img_to_array
from . import lib


class CnnModelSingleton:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if CnnModelSingleton.__instance is None:
            CnnModelSingleton()
        return CnnModelSingleton.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if CnnModelSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CnnModelSingleton.__instance = self
            self.model = None
            self.init_model(current_app.config['NUM_CLASS'])

    def init_model(self, class_unit=3):
        chanDim = -1
        self.model = Sequential()
        self.model.add(Conv2D(input_shape=(400, 700, 3), filters=16, kernel_size=(9, 9), padding="same", activation="relu"))
        self.model.add(BatchNormalization(axis=chanDim))
        self.model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

        self.model.add(Conv2D(filters=32, kernel_size=(7, 7), padding="same", activation="relu"))
        self.model.add(BatchNormalization(axis=chanDim))
        self.model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))
        # model.add(Dropout(rate=0.25))

        self.model.add(Conv2D(filters=64, kernel_size=(5, 5), padding="same", activation="relu"))
        self.model.add(BatchNormalization(axis=chanDim))
        self.model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

        self.model.add(Conv2D(filters=128, kernel_size=(5, 5), padding="same", activation="relu"))
        self.model.add(BatchNormalization(axis=chanDim))
        self.model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))
        # model.add(Dropout(rate=0.25))

        self.model.add(Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
        self.model.add(BatchNormalization(axis=chanDim))
        self.model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

        self.model.add(Flatten())
        self.model.add(Dense(units=4096, activation="relu"))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(rate=0.25))
        self.model.add(Dense(units=1024, activation="relu"))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(rate=0.25))
        self.model.add(Dense(units=256, activation="relu"))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(rate=0.25))
        self.model.add(Dense(units=64, activation="relu"))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(rate=0.25))
        self.model.add(Dense(units=8, activation="relu"))
        self.model.add(BatchNormalization())
        self.model.add(Dropout(rate=0.25))
        self.model.add(Dense(units=class_unit, activation="softmax"))

        opt = Adam(learning_rate=0.0005,
                   beta_1=0.8,
                   beta_2=0.9, )

        self.model.compile(optimizer=opt,
                           loss=keras.losses.categorical_crossentropy,
                           metrics=['accuracy'])
        model_path = os.path.join(current_app.instance_path, current_app.config['MODEL_PATH'])
        self.model.load_weights(model_path)

    def predict_image(self, img_path):
        # load the model
        image = load_img(img_path)
        input_arr = np.array([img_to_array(image)])
        c_pred = np.argmax(self.model.predict(input_arr))
        # remove keras objects in memory
        string_class = lib.map_index_to_string_class(c_pred)
        html_class = lib.map_index_to_included_html(c_pred)
        return string_class, html_class
