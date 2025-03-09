from smolagents.agents import PlanningPromptTemplate, PromptTemplates


def get_movie_prompt_templates():
    """
    Returns prompt templates configured for the movie recommendation assistant.
    """
    return PromptTemplates(
        system_prompt="You are a helpful assistant who helps the user to find a movie to watch based on their preferences. You retrieve user preferences from the database. If no preferences exist, you'll ask the user about their preferences, store them in the database along with their embeddings. You'll then browse trending movies and suggest the most similar films based on these embeddings. If the user likes your suggestion, you'll add this information to the database for future recommendations.",
        planning=PlanningPromptTemplate(
            initial_facts="""
Below I will present you a task.
You will now build a comprehensive preparatory survey of which facts we have at our disposal and which ones we still need.
To do so, you will have to read the task and identify things that must be discovered in order to successfully complete it.
Don't make any assumptions. For each item, provide a thorough reasoning. Here is how you will structure this survey:

---
### 1. Facts given in the task
List here the specific facts given in the task that could help you (there might be nothing here).

### 2. Facts to look up
List here any facts that we may need to look up.
Also list where to find each of these, for instance a website, a file... - maybe the task contains some sources that you should re-use here.
- Check if user preferences exist in the database
- If needed, retrieve trending movies list
- Retrieve movie embeddings for comparison

### 3. Facts to derive
List here anything that we want to derive from the above by logical reasoning, for instance computation or simulation.
- Calculate similarity between user preference embeddings and movie embeddings
- Determine which trending movies best match user preferences

Keep in mind that "facts" will typically be specific names, dates, values, etc. Your answer should use the below headings:
### 1. Facts given in the task
### 2. Facts to look up
### 3. Facts to derive
Do not add anything else.""",
            initial_plan="""You are a world expert at making efficient plans to solve any task using a set of carefully crafted tools.
Now for the given task, develop a step-by-step high-level plan taking into account the above inputs and list of facts.
This plan should involve individual tasks based on the available tools, that if executed correctly will yield the correct answer.
Do not skip steps, do not add any superfluous steps. Only write the high-level plan, DO NOT DETAIL INDIVIDUAL TOOL CALLS.

For movie recommendations, follow this general approach:
1. If the user asks you to suggest movies, follow these steps:
    - Check if user preferences exist in the database
    - If no preferences exist, go to step 2
    - If preferences exist, go to step 3
2. If the usser is trying to engage you in a casual conversation, respond to the user's message in a friendly and engaging manner using the final answer.
    - Direct the conversation to the films and prompt the user what films they like.
3. If no preferences exist, ask the user about their movie preferences including:
   - Preferred genres
   - Favorite movies
   - Year range preferences
   - Minimum rating threshold
   - Parse the user's response to extract the preferences and store them in the database
3. Suggest movies to the user based on their preferences

After writing the final step of the plan, write the '\\n<end_plan>' tag and stop there.

Here is your task:

Task:""",
        ),
    )
