#!/bin/bash

flask --app backaind db upgrade

if [ -n "$OWNAI_ROOT_USER" ] && [ -n "$OWNAI_ROOT_PASSWORD" ]; then
    flask --app backaind add-user --username $OWNAI_ROOT_USER --password $OWNAI_ROOT_PASSWORD
fi

gunicorn -b 0.0.0.0:5000 --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 "backaind:create_app()"
