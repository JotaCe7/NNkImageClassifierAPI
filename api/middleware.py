import json
import time
from uuid import uuid4
import uuid

import redis
import settings


# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
      host=settings.REDIS_IP, 
      port=settings.REDIS_PORT, 
      db=settings.REDIS_DB_ID
    )


# # Queue name
# REDIS_QUEUE = "service_queue"
# # Port
# REDIS_PORT = 6379
# # DB Id
# REDIS_DB_ID = 0
# # Host IP
# REDIS_IP = os.getenv("REDIS_IP", "redis")
# # Sleep parameters which manages the
# # interval between requests to our redis queue
# API_SLEEP = 0.05



def model_predict(image_name):
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
    # prediction = None
    # score = None

    # Assign an unique ID for this job and add it to the queue.
    # We need to assing this ID because we must be able to keep track
    # of this particular job across all the services
    # TODO
    job_id = str(uuid4())

    # Create a dict with the job data we will send through Redis having the
    # following shape:
    # {
    #    "id": str,
    #    "image_name": str,
    # }
    # TODO
    job_data = {
      "id": job_id,
      "image_name": image_name  
    }
    print(job_data)

    # Send the job to the model service using Redis
    # Hint: Using Redis `lpush()` function should be enough to accomplish this.
    # TODO
    db = redis.Redis(
          host=settings.REDIS_IP, 
          port=settings.REDIS_PORT, 
          db=settings.REDIS_DB_ID
        )
    db.lpush(settings.REDIS_QUEUE, json.dumps(job_data))

    # Loop until we received the response from our ML model
    while True:
        # Attempt to get model predictions using job_id
        # Hint: Investigate how can we get a value using a key from Redis
        # TODO
        output = None
        ml_service_response = db.get(job_id)
        if ml_service_response is None:
          continue
        ml_service_response_dict = json.loads(ml_service_response)
        prediction = ml_service_response_dict["prediction"]
        score = ml_service_response_dict["score"]

        # Don't forget to delete the job from Redis after we get the results!
        # Then exit the loop
        # TODO
        db.delete(job_id)

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)
        break
    
    return prediction, round(float(score),4)
    

# if __name__ == "__main__":
#   db = redis.Redis(
#     host="0.0.0.0", 
#     port="6379", 
#     db=0
#   )
#   print(db.ping())
