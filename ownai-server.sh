#!/bin/bash

if ! command -v flask &> /dev/null || ! command -v gunicorn &> /dev/null
then
    echo "Welcome to ownAI!"
    echo "Please install the dependencies first. This is how you can do it:"
    echo "    python3 -m venv venv"
    echo "    source venv/bin/activate"
    echo "    pip install -r requirements.txt"
    echo "Then run this script again."
    echo ""
    echo "Alternatively, you can also run ownAI in a Docker container."
    echo "To do so, configure the server by copying the .env.template file to .env and then editing the .env file."
    echo "Then run the following commands (replace <your-username> and <your-password>):"
    echo "    docker build -t ownai ."
    echo "    docker run --name ownai --env OWNAI_ROOT_USER=<your-username> --env OWNAI_ROOT_PASSWORD=<your-password> --env-file ./.env -p 5000:5000 ownai"
    echo "This is only required for the first run."
    echo "To start the server again just run:"
    echo "    docker start ownai"
    exit 1
fi

if [ -f ".env" ]
then
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

if [ -z "$OWNAI_DATABASE" ]
then
    echo "Please set environment variables to configure ownAI."
    echo "You can do this e.g. by copying the .env.template file to .env and then editing the .env file."
    exit 1
fi

if [ ! -f "$OWNAI_DATABASE" ]
then
    if [ -z "$OWNAI_ROOT_USER" ] || [ -z "$OWNAI_ROOT_PASSWORD" ]
    then
        echo "We still need to set up the database and add a first user."
        echo "To do so, you can do ONE of the following:"
        echo ""
        echo "- Execute the following commands:"
        echo "    flask init-db"
        echo "    flask add-user"
        echo "- OR set the environment variables OWNAI_ROOT_USER and OWNAI_ROOT_PASSWORD"
        echo "  (only required for the first run)"
        echo "- OR in case you are running ownAI in a Docker container:"
        echo "  (replace <your-username> and <your-password>)"
        echo "    docker run --name ownai --env OWNAI_ROOT_USER=<your-username> --env OWNAI_ROOT_PASSWORD=<your-password> --env-file ./.env -p 5000:5000 ownai"
        echo "  (only required for the first run, to start the server again just run: docker start ownai)"
        exit 1
    fi

    flask --app backaind init-db
    flask --app backaind add-user --username $OWNAI_ROOT_USER --password $OWNAI_ROOT_PASSWORD
fi

gunicorn -b 0.0.0.0:5000 --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 "backaind:create_app()"
