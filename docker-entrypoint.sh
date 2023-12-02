#!/bin/bash

flask --app backaind db upgrade

if [ -n "$OWNAI_DOWNLOAD_REPO" ] && [ -n "$OWNAI_DOWNLOAD_FILE" ]; then
    flask --app backaind download-model --repo $OWNAI_DOWNLOAD_REPO --filename $OWNAI_DOWNLOAD_FILE
fi

if [ -n "$OWNAI_ADD_AI" ]; then
    IFS=":" read -ra filepaths <<< "$OWNAI_ADD_AI"
    for filepath in "${filepaths[@]}"; do
        flask --app backaind add-ai --aifile "$filepath"
    done
fi

if [ -n "$OWNAI_ROOT_USER" ] && [ -n "$OWNAI_ROOT_PASSWORD" ]; then
    flask --app backaind add-user --username $OWNAI_ROOT_USER --password $OWNAI_ROOT_PASSWORD
fi

gunicorn -b 0.0.0.0:5000 --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 "backaind:create_app()"
