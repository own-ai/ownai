FROM python:3.10
WORKDIR /ownai
COPY backaind backaind
COPY examples examples
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY ownai-server.sh .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["./ownai-server.sh"]
