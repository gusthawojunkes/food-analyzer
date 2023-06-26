import re
import os
import tensorflow as tf
from pyunpack import Archive
from keras.models import load_model

modelDirectory = 'algorithm/model.h5'
exist = os.path.exists(modelDirectory)

def predict(time_stamp):
    print('inicio do predict: '+time_stamp)
    batch_size = 32
    image_size = (80, 80)

    ds_predict = tf.keras.preprocessing.image_dataset_from_directory('./algorithm/predict/'+time_stamp, 
                                                                     labels='inferred', 
                                                                     shuffle = True,
                                                                     color_mode='rgb', 
                                                                     batch_size=batch_size, 
                                                                     image_size=image_size, 
                                                                     seed=1234,
                                                                     validation_split=0.2, 
                                                                     subset="validation")

    if exist == False: 
        Archive('algorithm/model.rar').extractall('algorithm/')
    model = load_model('./algorithm/model.h5')
    

    predictions = model.predict(ds_predict)

    class_names=['apple', 'apple_braeburn_1', 'apple_crimson_snow_1', 'apple_golden_1', 'apple_golden_2', 'apple_golden_3', 'apple_granny_smith_1', 'apple_hit_1', 'apple_pink_lady_1', 'apple_red_1', 'apple_red_2', 'apple_red_3', 'apple_red_delicios_1', 'apple_red_yellow_1', 'apple_rotten_1', 'cabbage_white', 'carrot', 'cucumber', 'cucumber_3', 'eggplant_violet', 'pear', 'pear_3', 'zucchini', 'zucchini_dark_1']

    namePredicted = ''
    namePredicted = class_names[predictions[0].argmax()]
    namePredicted = namePredicted.replace('_',' ')
    namePredicted = re.sub('[0-9]','',namePredicted)

    return namePredicted