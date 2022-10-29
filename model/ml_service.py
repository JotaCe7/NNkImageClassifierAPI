import json
import os
import time

import numpy as np
import redis
import settings
import tensorflow
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# Connect to Redis and assign to variable `db``
db = redis.Redis(
      host=settings.REDIS_IP, 
      port=settings.REDIS_PORT, 
      db=settings.REDIS_DB_ID
    )
import ssl

#ssl._create_default_https_context = ssl._create_unverified_context
# Load Resnet50 model
model = MobileNetV2(include_top=True, weights=None)
#model = ResNet50(include_top=True, weights="/src/resnet50_weights_tf_dim_ordering_tf_kernels.h5")


def predict(image_name):
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
    # Load image and preprocess it
    file_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
    img = image.load_img(file_path, target_size=(224,224))
    x = image.img_to_array(img)
    x_batch = np.expand_dims(x, axis=0)
    x_batch = preprocess_input(x_batch)

    # Make predictions and keep the one with highest probability
    preds = model.predict(x_batch)
    best_pred = decode_predictions(preds, top=1)
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
    print("START ML")
    while True:
        # Take a new job from Redis
      queue_name, job_data_str = db.brpop(settings.REDIS_QUEUE)
      print(job_data_str)
      
      job_data = json.loads(job_data_str.decode('utf-8'))

      # Run ML model on the given data
      class_name, pred_probability = predict(job_data['image_name'])
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
