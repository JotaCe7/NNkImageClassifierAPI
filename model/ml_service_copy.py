# import json
# import os
# import time

# import numpy as np
# import redis
# import settings

# from tensorflow.keras.applications import ResNet50
# from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
# from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = None

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = None


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
    class_name = None
    pred_probability = None
    # TODO

    return class_name, pred_probability


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

        # Don't forget to sleep for a bit at the end
        #print("You shoud not be seeing this yet!")
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main2__":
    # Now launch process
    model = ResNet50(include_top=True, weights="imagenet")
    #model.summary()
    img = image.load_img("./tests/dog.jpeg", target_size=(224,224))
    x = image.img_to_array(img)
    x_batch = np.expand_dims(x, axis=0)
    x_batch = preprocess_input(x_batch)
    preds = model.predict(x_batch)
    best_pred = decode_predictions(preds, top=1)
    print(best_pred[0][0][1])


    print("Launching ML service...")
    #classify_process()


def keypad_string2(keys:str):
  keypad = {"1":"", "2": "abc", "3":"def", "4":"ghi", "5":"jkl", "6":"mno", "7":"pqrs", "8":"tuv","9":"wxyz","0":" "}
  output = ''
  final_list = []
  inner_i = 0
  keys.replace("1","")
  if keys=="":
    return output
  c_prev = keys[0]
  for c  in keys[1:]:
    if c == c_prev:
      if inner_i<len(keypad[c])-1:
        inner_i = inner_i + 1
      else:
        final_list.append([c_prev, inner_i])
        inner_i=0
    else:
      final_list.append([c_prev, inner_i])
      c_prev = c
      inner_i=0
  final_list.append([c_prev, inner_i])
  for l in final_list:
    if l[0]!='1':
      output = output + keypad[l[0]][l[1]]
  return output



def keypad_string(keys):
  keypad = [{"2": "abc", "3":"def", "4":"ghi"}]
  output = ''
  final_list = [["a", 2], ["c",1], ]
  inner_i = 0
  c_prev=""
  for c in keys:
    print(c)
    print(c_prev)

    if c==c_prev:
      inner_i+=1
      if inner_i <=2:
        continue
      else:
        c_prev=''
    else:
      c_prev = c
    
    final_list.append([c,inner_i])
    inner_i = 0
    
    
    
  return final_list


if __name__ == "__main__":
    print(keypad_string2("12345"))
    print(keypad_string2("4433555555666"))
    print(keypad_string2("2022"))
    print(keypad_string2(""))
    print(keypad_string2("111"))
    pass