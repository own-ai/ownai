# ownAI

With ownAI you can run your own AIs.

ownAI is an open-source platform written in Python using the Flask framework. It allows you to host and manage AI applications with a web interface for interaction. ownAI supports the customization of AIs for specific use cases and provides a flexible environment for your AI projects.

## Table of Contents

- [Features](#features)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Production setup](#production-setup)
- [Development setup](#development-setup)
- [Usage](#usage)
- [AI files](#ai-files)
- [Contributing](#contributing)
- [License](#license)

## Features

- Host and manage AI applications
- Web-based interface for interacting with AI models
- Support for AI customization to suit specific needs
- Create and manage additional knowledge for AIs
- Open-source and community-driven

## Quick start

To get started quickly, clone this repository to your Linux server and execute:

```
./ownai-server.sh
```

This will guide you through the installation process and start the server.
For a detailed installation guide, please refer to the following section.

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
flask add-user
```

8. Start the server:

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

If you want to get started quickly and run your AIs by yourself, please have a look at the [ctransformers](./examples/ctransformers/), [gpt4all](./examples/gpt4all/) and [huggingface_pipeline](./examples/huggingface_pipeline/) examples.
These allow you to run your own AIs on your machine with little or no further setup.

If you want to create your own aifiles, have a look at the [aifilemaker.py](./aifilemaker.py) script, which you can use as a starting point.

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
