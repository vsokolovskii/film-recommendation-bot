from faker import Faker
from locust import HttpUser, between, task

fake = Faker()


class LLMChatUser(HttpUser):
    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)

    def on_start(self):
        """Initialize the user"""
        pass

    @task(10)
    def ask_question(self):
        """Send a question to the API"""
        # Generate a random question with length between 10 and 100 characters
        question = fake.text(max_nb_chars=100)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        payload = {"text": question}

        with self.client.post(
            "/question", json=payload, headers=headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 422:
                # Input validation error - expected for some random inputs
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
