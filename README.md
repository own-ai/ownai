# ownAI

With ownAI you can run your own AIs.

ownAI is an open-source platform written in Python using the Flask framework. It allows you to host and manage AI applications with a web interface for interaction. ownAI supports fine-tuning AI models for specific use-cases and provides a flexible environment for your AI projects.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Fine-tuning Models](#fine-tuning-models)
- [Contributing](#contributing)
- [License](#license)

## Features

- Host and manage AI applications with ease
- Web-based interface for interacting with AI models
- Support for model fine-tuning to suit specific needs
- Open-source and community-driven

## Installation

ownAI requires Python 3.8 or higher. To install and set up ownAI, follow these steps:

1. Clone the repository:
```
git clone https://github.com/own-ai/ownAI.git
```

2. Enter the project directory:
```
cd ownAI
```

3. Create a virtual environment and activate it:
```
python3 -m venv venv
source venv/bin/activate
```

4. Install requirements:
```
pip install -r requirements.txt
```

5. Configure the server by copying the `.env.template` file to `.env` and then editing the `.env` file.

6. Initialize the database:
```
flask init-db
```

7. Register a new user:
```
flask register-user
```

8. Start the server:
```
flask run
```

Now, you should be able to access the ownAI web interface at `http://localhost:5000`.

## Usage

To interact with the ownAI server, visit the web interface at `http://localhost:5000` and follow these steps:

1. Select an AI model from the dropdown menu.

2. Enter your input text or data in the provided input box.

3. Click the "Submit" button to process your input with the selected AI model.

4. The AI model's response will be displayed in the output section.

## Fine-tuning Models

ownAI supports fine-tuning AI models for specific use-cases. To fine-tune a model, follow these steps:

1. Prepare your training data in the required format.

2. Configure the fine-tuning settings in the `instance/config.py` file.

3. Run the fine-tuning script:
```
python finetune.py
```

4. Monitor the training process and evaluate the results.

5. Once the fine-tuning is complete, the new model will be available for use in the web interface.

## Contributing

We welcome contributions from the community. To contribute, please:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Commit your changes
4. Open a pull request

Please follow the coding style guidelines and ensure your changes are well-documented.
Thank you very much for your contribution!

## License

ownAI is released under the [MIT License](LICENSE.txt).
