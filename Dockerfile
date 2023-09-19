FROM python:3.10
WORKDIR /ownai
COPY backaind backaind
COPY examples examples
COPY migrations migrations
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY docker-entrypoint.sh .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["./docker-entrypoint.sh"]
