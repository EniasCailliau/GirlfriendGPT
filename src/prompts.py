PERSONALITY_PROMPT = """{personality}

TOOLS:
------

You have access to the following tools:

"""

FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a final response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
{ai_prefix}: [your final response here which ALWAYS includes UUID of generated images]

Make sure to use all observations to come up with your final response. 
ALWAYS copy the UUID of images into your final response!
ALWAYS come up with a final response after generating an image and make sure to include the UUID of that image.
```"""

SUFFIX = """Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}"""
