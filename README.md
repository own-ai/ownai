# ownAI

With ownAI you can run your own AIs.

ownAI is an open-source platform written in Python using the Flask framework. It allows you to host and manage AI applications with a web interface for interaction. ownAI supports the customization of AIs for specific use cases and provides a flexible environment for your AI projects.

For a demo installation and a managed private cloud service, please visit [https://ownai.org](https://ownai.org).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Production setup](#production-setup)
- [Development setup](#development-setup)
- [Usage](#usage)
- [AI files](#ai-files)
- [Updating](#updating)
- [Run with Docker](#run-with-docker)
- [Contributing](#contributing)
- [License](#license)

## Features

- Host and manage AI applications
- Web-based interface for interacting with AI models
- Support for AI customization to suit specific needs
- Create and manage additional knowledge for AIs
- Open-source and community-driven

## Installation

ownAI requires Python 3.8 or higher. Due to a dependency issue, it does not currently run on Python 3.11. To install and set up ownAI, follow these steps:

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
flask db upgrade
```

7. Register a new user:

```
flask add-user
```

8. Optionally: Set up your first AI. We recommend starting with the Llama 2 model and the _Helpful Assistant_ example.

Download the model (this needs about 4 GB of disk space):

```
flask download-model --repo "TheBloke/Llama-2-7B-Chat-GGUF" --filename "llama-2-7b-chat.Q4_K_M.gguf"
```

Add the AI:

```
flask add-ai --aifile ./examples/llamacpp/helpful_assistant.aifile
```

9. Start the server:

```
flask run
```

Now, you should be able to access the ownAI web interface at `http://localhost:5000`.

## Production setup

For a production setup, we recommend using a WSGI server such as Gunicorn.
If you followed the steps above, Gunicorn is already installed in your virtual environment.
To start the server, run:

```
gunicorn -b 0.0.0.0:5000 --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 "backaind:create_app()"
```

We recommend using a reverse proxy such as nginx to handle HTTPS.

## Development setup

If you want to contribute to the ownAI frontend, you can set up a development environment as follows:

1. Install Node.js and npm.
2. Install the frontend dependencies:

```
npm install
```

3. Start the development server (this already includes starting the Flask backend server):

```
npm run dev
```

## Usage

To start interacting with your own AI, visit the web interface at `http://localhost:5000` and follow these steps:

1. Log in using the credentials you set up during installation.

2. Click on the ownAI logo in the upper left corner to open the main menu.

3. Choose "AI Workshop" and click the "New AI" button.

4. Load an Aifile (see [below](#ai-files) for details and in the [examples directory](./examples) for examples).

5. Optionally customize the AI to suit your needs.

6. Optionally select "Knowledge" from the main menu to upload additional knowledge (if your AI chain supports it).

7. Select "Interaction" from the main menu and enter your input text or data in the provided input box.

## AI files

ownAI uses `.aifile` files to store and load the specification and configuration of AIs.
In the [examples directory](./examples) you can find many different examples to run various AI models locally or to use external providers.

Please also refer to the [readme file](./examples/README.md) in the examples directory.

If you want to get started quickly and run your AIs by yourself, please have a look at the [llamacpp](./examples/llamacpp/) examples.
These allow you to run your own AIs on your machine with little or no further setup.

If you want to create your own aifiles, have a look at the [aifilemaker.py](./aifilemaker.py) script, which you can use as a starting point.

## Updating

To update ownAI, simply pull the latest changes from the repository and run:

```
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
```

## Run with Docker

If you have Docker installed, you can run ownAI in a Docker container.
Otherwise please follow the [installation](#installation) section.

To run ownAI with Docker, first configure the server by downloading the `.env.template` file.
Rename the file to `docker.env` and edit the file.
Then run the following command (replace `<your-username>` and `<your-password>`):

```
docker run --name ownai --env OWNAI_ROOT_USER=<your-username> --env OWNAI_ROOT_PASSWORD=<your-password> --env OWNAI_DOWNLOAD_REPO="TheBloke/Llama-2-7B-Chat-GGUF" --env OWNAI_DOWNLOAD_FILE="llama-2-7b-chat.Q4_K_M.gguf" --env-file ./docker.env -p 5000:5000 ownai/ownai
```

This is only required for the first run. To start the server again just run:

```
docker start ownai
```

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
