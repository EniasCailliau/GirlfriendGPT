from langchain.agents.mrkl.output_parser import MRKLOutputParser

FINAL_ANSWER_ACTION = "Final Answer:"

FORMAT_INSTRUCTIONS_W_TOOLS = """
Use the following format:

Input: the input question you must answer
Thought: you should always think about what to do. When it's a casual conversation, skip to Final Answer and do not add Action,Action Input, or Observation:
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input. Consider all observations to come up with a final answer.
"""

FORMAT_INSTRUCTIONS_WO_TOOLS = """
Use the following format:

Question: the input question you must answer
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""


def get_format_instructions(has_tools=True) -> str:
    return FORMAT_INSTRUCTIONS_W_TOOLS if has_tools else FORMAT_INSTRUCTIONS_WO_TOOLS


class CustomParser(MRKLOutputParser):
    def get_format_instructions(self) -> str:
        return get_format_instructions(True)
