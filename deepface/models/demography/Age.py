import os
import gdown
import numpy as np
from deepface.models.facial_recognition import VGGFace
from deepface.commons import package_utils, folder_utils
from deepface.models.Demography import Demography
from deepface.commons.logger import Logger

logger = Logger()

# ----------------------------------------
# dependency configurations

tf_version = package_utils.get_tf_major_version()

if tf_version == 1:
    from keras.models import Model, Sequential
    from keras.layers import Convolution2D, Flatten, Activation
else:
    from tensorflow.keras.models import Model, Sequential
    from tensorflow.keras.layers import Convolution2D, Flatten, Activation

# ----------------------------------------

# pylint: disable=too-few-public-methods
class ApparentAgeClient(Demography):
    """
    Age model class
    """

    def __init__(self):
        self.model = load_model()
        self.model_name = "Age"

    def predict(self, img: np.ndarray) -> np.float64:
        # model.predict causes memory issue when it is called in a for loop
        # age_predictions = self.model.predict(img, verbose=0)[0, :]
        age_predictions = self.model(img, training=False).numpy()[0, :]
        return find_apparent_age(age_predictions)


def load_model(
    url="https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5",
) -> Model:
    """
    Construct age model, download its weights and load
    Returns:
        model (Model)
    """

    model = VGGFace.base_model()

    # --------------------------

    classes = 101
    base_model_output = Sequential()
    base_model_output = Convolution2D(classes, (1, 1), name="predictions")(model.layers[-4].output)
    base_model_output = Flatten()(base_model_output)
    base_model_output = Activation("softmax")(base_model_output)

    # --------------------------

    age_model = Model(inputs=model.input, outputs=base_model_output)

    # --------------------------

    # load weights

    home = folder_utils.get_deepface_home()
    output = os.path.join(home, ".deepface/weights/age_model_weights.h5")

    if not os.path.isfile(output):
        logger.info(f"{os.path.basename(output)} will be downloaded...")
        gdown.download(url, output, quiet=False)

    age_model.load_weights(output)

    return age_model

    # --------------------------


def find_apparent_age(age_predictions: np.ndarray) -> np.float64:
    """
    Find apparent age prediction from a given probas of ages
    Args:
        age_predictions (?)
    Returns:
        apparent_age (float)
    """
    output_indexes = np.arange(0, 101)
    apparent_age = np.sum(age_predictions * output_indexes)
    return apparent_age
