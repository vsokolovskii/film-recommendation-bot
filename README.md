# Movie Recommendation Bot

A FastAPI application that provides a chat interface for the agent which can assist the user to choose the film to watch based on their preferences.

## Prerequisites


### uv Package Manager
* We need to install the uv package manager locally to manage dependencies in the .venv
* To install follow: https://docs.astral.sh/uv/getting-started/installation/

### just
* To install follow: https://github.com/casey/just

### LLM
* To stay LLM agnostic, we use the OpenAI interface so that we can easily switch to any other LLM that supports the OpenAI interface.
    * You can even use the OpenAI API directly, adjust the .env file with the correct API key, host and model name.
* Ollama for local development is the ideal setup.
* To install Ollama follow: https://ollama.com/download

### pre-commit
* If you are planning to contribute to the project, you will need to install pre-commit hooks.
* To install follow: https://pre-commit.com/#install

## Setup
```
# Copy the .env.example file to .env and update the .env file with the correct LLM details.
cp .env.example .env

# Create .venv and install dependencies
uv sync

# Install pre-commit hooks
pre-commit install

# Start ollama
just ollama llama3.2
# you can use any other model supported by ollama. If you are using a different LLM then make sure to update the .env file with the correct LLM details.

# Run server
just server
```

## Testing
```
just test  # runs unit tests

curl -X 'POST'   'http://0.0.0.0:8080/question'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
  "text": "hey, i like matrix and american pie, what would you recommend?"
}'
```

If you open http://0.0.0.0:8080 you will be redirected to the SwaggerUI where you can test the API.

You can also open the telegram bot to talk to the Movie Recommender @rohlik_movie_recommender_bot


## Known issues and limitations
* Bot is launched from the main app entrypoint.
* The preferences is just one table where each user can have only one row basically, ideally we would track different preferences of one user based on time for instance.
* Smolagent does not have the async interface by default, so the app will not be easily scalable.
* How the recommendation system works is suboptimal, it filters out by genres and years first and then does the embedding similarity, ideally we would extract some features from the description of the film from the wiki, not the film overview since it can be misleading very often.
* In general the app is very raw since I developed it in a couple of days for the Rohlik task.



## Profiling
Before running the profiling make sure to run the server with `just server`.
To run the profiling UI use `just profile`.


* You can use Locust to profile the API.

