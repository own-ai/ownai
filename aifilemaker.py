#!/usr/bin/env python3
"""Simple example how to quickly create Aifiles."""
import json
from langchain.chains import LLMChain
from langchain.chains.loading import load_chain_from_config
from langchain.llms.fake import FakeListLLM
from langchain.prompts import PromptTemplate

# 1. Set a name for your AI
NAME = "Fake AI"

# 2. Set up the LLM you want to use
# (see https://python.langchain.com/en/latest/modules/models/llms/integrations.html for examples)
llm = FakeListLLM(responses=["Hello", "Bye"])

# 3. Set up a prompt template for your LLM and task
# (see https://python.langchain.com/en/latest/modules/prompts/prompt_templates/getting_started.html)
# Consider using a template that suits your model!
# Check the models page on Hugging Face etc. to get a correct prompting template.
TEMPLATE = """Question: {input_text}
Answer:"""
prompt = PromptTemplate(template=TEMPLATE, input_variables=["input_text"])

# 4. Set up the chain
# (see https://python.langchain.com/en/latest/modules/chains.html)
llm_chain = LLMChain(prompt=prompt, llm=llm, output_key="output_text")

# Test if loading the chain again works
load_chain_from_config(llm_chain.dict())

# Export Aifile
aifile_dict = {"name": NAME, "aifileversion": 1, "chain": llm_chain.dict()}
aifile = json.dumps(aifile_dict, indent=2)
print(aifile)
