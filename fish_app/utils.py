from flask import current_app
from skimage.io import imread
import time, random, string
import locale


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def pad_timestamp(filename):
    name = filename.split('.')
    return name[0] + str(round(time.time())) + '.' + name[1]


def generate_passphrase(length):
    letters = string.ascii_letters
    return ''.join(random.choices(letters)[0] for i in range(length))


def number_to_currency(x):
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    return locale.currency(x, grouping=True)


def check_image_size(path):
    """
    Check image dimension
    @param path: image pah
    @return: true if dim match else false
    """
    img = imread(path)
    # take first two dims of img, when using img.shape it will return height first than width
    size = img.shape
    current_app.logger.info("image size: " + " ".join(str(x) for x in size))
    return True if size[1] == current_app.config["ALLOWED_IMG_WIDTH"] and size[0] == \
                   current_app.config["ALLOWED_IMG_HEIGHT"] else False
