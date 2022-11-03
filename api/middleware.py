import json
import time
from uuid import uuid4

import redis
import settings

# Connect to Redis
db = redis.Redis( host=settings.REDIS_IP, 
                  port=settings.REDIS_PORT, 
                  db=settings.REDIS_DB_ID
                )


def model_predict(image_name, NNmodel='ResNet50'):
  """
  Receives an image name and queues the job into Redis.
  Will loop until getting the answer from our ML service.

  Parameters
  ----------
  image_name : str
    Name for the image uploaded by the user.

  Returns
  -------
  prediction, score : tuple(str, float)
    Model predicted class as a string and the corresponding confidence
    score as a number.
  """
  prediction = None
  score = None

  # Assign an unique ID for this job and add it to the queue.
  job_id = str(uuid4())
  job_data = {"id": job_id, "image_name": image_name, "NNmodel": NNmodel}
  
  # Send the job to the model service using Redis
  db.lpush(settings.REDIS_QUEUE, json.dumps(job_data))

  # Loop until we received the response from our ML model
  while True:

    # Attempt to get model predictions using job_id
    response = db.get(job_id)
    if response is None:
      # Sleep some time waiting for model results
      time.sleep(settings.API_SLEEP)
      continue
    response_dict = json.loads(response)
    prediction = response_dict["prediction"]
    score = response_dict["score"]

    # Delete the job from Redis
    db.delete(job_id)
    break
  
  return prediction, round(float(score),4)
