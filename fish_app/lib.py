import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from flask import current_app


def log_info(train_generator):
    # Label mapping
    classes = train_generator.class_indices

    label_map = np.array(list(classes.items()))

    label = label_map[:, 0].tolist()
    label_id = label_map[:, 1].tolist()

    current_app.logger.info(label_map)
    current_app.logger.info('\n')
    current_app.logger.info(label)
    current_app.logger.info('\n')

    current_app.logger.info(label_id)


def load_data(path, split_ratio=0.25, shuffle=True):
    train_datagen = ImageDataGenerator(validation_split=split_ratio)

    target_size = current_app.config['ALLOWED_IMG_WIDTH'], current_app.config['ALLOWED_IMG_HEIGHT']

    # data flow
    data_path = 'fish_dataset'  # input dataset
    train_generator = train_datagen.flow_from_directory(path,
                                                        target_size=target_size,
                                                        subset='training',
                                                        shuffle=shuffle
                                                        )

    val_generator = train_datagen.flow_from_directory(path,  # same directory as training data
                                                      target_size=target_size,
                                                      subset='validation',  # set as validation data
                                                      shuffle=shuffle
                                                      )
    return train_generator, val_generator


def map_index_to_string_class(index):
    """
    Helper class to turn int to String (class)
    @param index: id of a class
    @return: String
    """
    map_table = {0: "Abudefduf", 1: "Amphiprion", 2: "Chaetodon"}
    return map_table.get(index, "Class not found")


def map_index_to_included_html(index):
    """
    Helper class to turn index to html file to be included
    @param index: if of a class
    @return: String
    """
    map_table = {0: "genus_abudefduf.html", 1: "genus_amphiprion.html", 2: "genus_chaetodon.html"}
    return map_table.get(index, "Class not found")
