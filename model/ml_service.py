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

# In order to prevent long downloading time we have downloaded the weights for each model in
# weights folder. In case the weights are not present, download them in the go.

# 1. Create a weights folder inside model/,
# 2. Download https://drive.google.com/file/d/1JPzUUBuqtN0CEzWRC7A2jFfA73OWQMT5/view?usp=sharing, and
# 3. unzip it in the just created folder

try:
  ResNet50 = resnet50.ResNet50(include_top=True,
                               weights="/src/weights/resnet50_weights_tf_dim_ordering_tf_kernels.h5")
except:
  ResNet50 = resnet50.ResNet50(include_top=True,weights="imagenet")
try:
  ResNet101V2 = resnet_v2.ResNet101V2(include_top=True,
                                      weights='/src/weights/resnet101v2_weights_tf_dim_ordering_tf_kernels.h5')
except:
  ResNet101V2 = resnet_v2.ResNet101V2(include_top=True,weights="imagenet")
try:
  MobileNet = mobilenet.MobileNet(include_top=True,
                                  weights='/src/weights/mobilenet_1_0_224_tf.h5')
except:
  MobileNet = mobilenet.MobileNet(include_top=True,weights="imagenet")
try:
  Xception = xception.Xception(include_top=True,
                              weights='/src/weights/xception_weights_tf_dim_ordering_tf_kernels.h5')
except:
  Xception = xception.Xception(include_top=True,weights="imagenet")
try:
  VGG16 = vgg16.VGG16(include_top=True,
                      weights='/src/weights/vgg16_weights_tf_dim_ordering_tf_kernels.h5')
except:
  VGG16 = vgg16.VGG16(include_top=True,weights="imagenet")
  


def predict(image_name, NNmodel='ResNet50'):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.
    NNmodel : str
        Keras model name to use for prediction

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
      #print(job_data_str)
      
      job_data = json.loads(job_data_str.decode('utf-8'))

      # Run ML model on the given data
      try:
        class_name, pred_probability = predict(job_data['image_name'], job_data['NNmodel'])
      except:
        class_name, pred_probability = '', 0
      pred_dict = {
                    "prediction": class_name,
                    "score": pred_probability
                  }
      # Store the results on Redis
      db.set(job_data["id"], json.dumps(pred_dict))

      # Sleep for a bit at the end
      time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
