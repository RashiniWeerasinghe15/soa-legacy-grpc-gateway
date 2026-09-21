FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY soap_client/ ./soap_client/

CMD ["python", "soap_client/client.py"]