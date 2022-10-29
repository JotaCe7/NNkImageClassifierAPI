import json
import os
import time

import numpy as np
import redis
import settings
# from tensorflow.keras.applications import ResNet50, ResNet101V2 
# from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
# from tensorflow.keras.applications.resnet_v2 import  preprocess_input as preprocess_inputV2
# from tensorflow.keras.applications.resnet_v2 import  decode_predictions as decode_predictionsV2
from tensorflow.keras.applications import resnet50, resnet_v2, mobilenet, vgg16, xception



from tensorflow.keras.preprocessing import image



# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
      host=settings.REDIS_IP, 
      port=settings.REDIS_PORT, 
      db=settings.REDIS_DB_ID
    )
print("dssssd")

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
#model = ResNet50(include_top=True, weights="imagenet")


models= { 'ResNet50': resnet50,
          'ResNet101V2': resnet_v2 ,
          'MobileNet': mobilenet,
          'VGG16': vgg16,
          'Xception': xception}

ResNet50 = resnet50.ResNet50(include_top=True,
                             weights="/src/weights/resnet50_weights_tf_dim_ordering_tf_kernels.h5")
ResNet101V2 = resnet_v2.ResNet101V2(include_top=True,
                                    weights='/src/weights/resnet101v2_weights_tf_dim_ordering_tf_kernels.h5'
)
MobileNet = mobilenet.MobileNet(include_top=True,weights='imagenet')
Xception = xception.Xception(include_top=True, weights='imagenet')
VGG16 = vgg16.VGG16(include_top=True, weights='imagenet')

def predict(image_name, NNmodel='ResNet50'):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    input_shape = 299 if NNmodel == 'Xception' else 224
    file_path = os.path.join(settings.UPLOAD_FOLDER,image_name)
    img = image.load_img(file_path, target_size=(input_shape,input_shape))
    x = image.img_to_array(img)
    x_batch = np.expand_dims(x, axis=0)

    #x_batch = preprocess_input(x_batch)
    #preds = model.predict(x_batch)
    #best_pred = decode_predictions(preds, top=1)
    model = globals()[NNmodel]
    model_class= models[NNmodel]
    x_batch = model_class.preprocess_input(x_batch)
    preds = model.predict(x_batch)
    best_pred = model_class.decode_predictions(preds, top=1)
    

    
    class_name = best_pred[0][0][1]
    pred_probability = best_pred[0][0][2]
    # TODO
    return class_name, round(float(pred_probability),4)


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        queue_name, job_data_str = db.brpop(settings.REDIS_QUEUE)
        job_data = json.loads(job_data_str)

        class_name, pred_probability = predict(job_data['image_name'], 'Xception')
        pred_dict = {
                      "prediction": class_name,
                      "score": float(pred_probability),
                    }
        print(pred_dict)

        #time.sleep(10)
        db.set(job_data["id"], json.dumps(pred_dict))


        # Don't forget to sleep for a bit at the end
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
