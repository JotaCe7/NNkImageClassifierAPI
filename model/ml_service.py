import json
import os
import time

from PIL import Image

import numpy as np
import redis
import settings

from tensorflow.keras.applications import resnet50, resnet_v2, mobilenet, vgg16, xception
from tensorflow.keras.preprocessing import image

# Connect to Redis and assign to variable `db``
db = redis.Redis(
      host=settings.REDIS_IP, 
      port=settings.REDIS_PORT, 
      db=settings.REDIS_DB_ID
    )

# Load models
models= { 'ResNet50': resnet50,
          'ResNet101V2': resnet_v2 ,
          'MobileNet': mobilenet,
          'VGG16': vgg16,
          'Xception': xception}

ResNet50 = resnet50.ResNet50(include_top=True,
                             weights="/src/weights/resnet50_weights_tf_dim_ordering_tf_kernels.h5")
ResNet101V2 = resnet_v2.ResNet101V2(include_top=True,
                                    weights='/src/weights/resnet101v2_weights_tf_dim_ordering_tf_kernels.h5')
MobileNet = mobilenet.MobileNet(include_top=True,
                                weights='/src/weights/mobilenet_1_0_224_tf.h5')
Xception = xception.Xception(include_top=True,
                             weights='/src/weights/xception_weights_tf_dim_ordering_tf_kernels.h5')
VGG16 = vgg16.VGG16(include_top=True,
                    weights='/src/weights/vgg16_weights_tf_dim_ordering_tf_kernels.h5')


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
    # Load and correct its dimmension
    input_shape = 299 if NNmodel == 'Xception' else 224
    file_path = os.path.join(settings.UPLOAD_FOLDER,image_name)
    img = image.load_img(file_path, target_size=(input_shape,input_shape))
    x = image.img_to_array(img)
    x_batch = np.expand_dims(x, axis=0)

    # Preprocess inputm make prediction and keep the one with highest probability
    model = globals()[NNmodel]
    model_class= models[NNmodel]
    x_batch = model_class.preprocess_input(x_batch)

    # Save preprocessed image
    preprocessed_batch = (x_batch[0] + 128).astype(np.uint8)
    preprocessed_image = Image.fromarray(preprocessed_batch)
    preprocessed_image.save(os.path.join(settings.PREPROCESS_FOLDER,image_name))

    preds = model.predict(x_batch)
    best_pred = model_class.decode_predictions(preds, top=1)
    class_name = best_pred[0][0][1]
    pred_probability = best_pred[0][0][2]

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
        # Take a new job from Redis
      queue_name, job_data_str = db.brpop(settings.REDIS_QUEUE)
      print(job_data_str)
      
      job_data = json.loads(job_data_str.decode('utf-8'))

      # Run ML model on the given data
      class_name, pred_probability = predict(job_data['image_name'], job_data['NNmodel'])
      pred_dict = {
                    "prediction": class_name,
                    "score": float(pred_probability)
                  }
      # Store the results on Redis
      db.set(job_data["id"], json.dumps(pred_dict))

      # Sleep for a bit at the end
      time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
