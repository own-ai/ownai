# Hugging Face TextGen Inference

[Text Generation Inference](https://github.com/huggingface/text-generation-inference) is a Rust, Python and gRPC server for text generation inference.

This allows you to run [Hugging Face Hub models](https://huggingface.co/models) and other LLMs on your own infrastructure.

## Set up

- Set up the [Text Generation Inference server](https://github.com/huggingface/text-generation-inference).
- Set the `inference_server_url` setting in the aifile to the URL of your server.

## Privacy

These AIs are running on your own machine or on a server where you install the inference server.
