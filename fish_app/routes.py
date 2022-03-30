import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Markup, send_from_directory
)

from . import utils, CnnModel

from werkzeug.utils import secure_filename

bp = Blueprint('route', __name__, url_prefix='/')


@bp.route('/fish', methods=['GET'])
def fish_test():
    return render_template('fish.html')


@bp.route('/upload', methods=['GET'])
def upload_redirect():
    return redirect(url_for('route.fish_test'))


@bp.route('/upload', methods=['POST'])
def upload_and_identify():
    file = request.files['file']
    if file and utils.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = utils.pad_timestamp(filename)
        path = os.path.join(current_app.instance_path, current_app.config['UPLOAD_DIR'])

        try:
            os.makedirs(path)
            current_app.logger.debug("Directory " + path + " is created.")

        except OSError:
            pass

        filepath = os.path.join(path, filename)
        file.save(filepath)
        current_app.logger.debug(filepath + " saved successfully.")

        # now check image dims once the image stored to disk
        if utils.check_image_size(filepath):
            # classify this image
            model = CnnModel.CnnModelSingleton.getInstance()
            fish_genus, include_html = model.predict_image(filepath)
            current_app.logger.info("Predicted fish: " + fish_genus)
            # we need to pass image path here to load on the next refresh
            return render_template('fish.html', upload_flag=True, img_name=filename, predicted_fish=fish_genus,
                                   include_html=include_html)

        return render_template('fish.html', size_unmatch_flag=True)

    else:
        return render_template('fish.html', fail_upload_flag=True)


@bp.route('/get_image/<filename>')
def get_image(filename):
    """
    This function is used to retrieve image from disk and returned the static file for another usage
    """
    path = os.path.join(current_app.instance_path, current_app.config['UPLOAD_DIR'])
    return send_from_directory(path, filename)