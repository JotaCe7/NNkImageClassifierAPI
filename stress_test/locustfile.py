from locust import HttpUser, task, between


# class APIUser(HttpUser):

#     # Put your stress tests here.
#     # See https://docs.locust.io/en/stable/writing-a-locustfile.html for help.
#     # TODO
#     raise NotImplementedError
# import time
# from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(20)
    def predict_post(self):

      self.client.post("/predict",files={'file': open("../tests/dog.jpeg", "rb")})

    @task(1)
    def feedback_post(self):
      data = {
          "report": "{'filename': 'test', 'prediction': 'angora_cat', 'score': 0.95 }"
      }
      self.client.post("/feedback", data=data)



    def on_start(self):
      pass