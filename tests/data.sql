INSERT INTO user (username, passhash)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO ai (name, input_keys, chain)
VALUES
  ('OpenAssistant SFT-4 12B @HuggingFace-Hub', '["input_text"]', '{"memory": null, "verbose": false, "prompt": {"input_variables": ["input_text"], "output_parser": null, "partial_variables": {}, "template": "<|prompter|>{input_text}<|endoftext|><|assistant|>", "template_format": "f-string", "validate_template": true, "_type": "prompt"}, "llm": {"repo_id": "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5", "task": null, "model_kwargs": {"max_new_tokens": 200}, "_type": "huggingface_hub"}, "output_key": "output_text", "_type": "llm_chain"}'),
  ('OpenAssistant SFT-4 12B with knowledge @HuggingFace-Hub', '["input_text", "input_knowledge"]', '{"memory": null, "callbacks": null, "callback_manager": null, "verbose": false, "input_key": "input_knowledge", "output_key": "output_text", "llm_chain": {"memory": null, "callbacks": null, "callback_manager": null, "verbose": false, "prompt": {"input_variables": ["summaries", "input_text"], "output_parser": null, "partial_variables": {}, "template": "<|prompter|>Please answer this question: {input_text}\nUse the following information:\n{summaries}\n<|endoftext|><|assistant|>", "template_format": "f-string", "validate_template": true, "_type": "prompt"}, "llm": {"repo_id": "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5", "task": null, "model_kwargs": {"max_new_tokens": 200}, "_type": "huggingface_hub"}, "output_key": "text", "_type": "llm_chain"}, "document_prompt": {"input_variables": ["page_content", "source"], "output_parser": null, "partial_variables": {}, "template": "Context: {page_content}\nSource: {source}", "template_format": "f-string", "validate_template": true, "_type": "prompt"}, "document_variable_name": "summaries", "document_separator": "\n\n", "_type": "stuff_documents_chain"}');

INSERT INTO knowledge (name, embeddings, persist_directory)
VALUES
  ('Test 1', 'huggingface', 'instance/knowledge'),
  ('Test 2', 'huggingface', 'instance/knowledge2');
