FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY banking_service_pb2.py .
COPY banking_service_pb2_grpc.py .
COPY gateway/ ./gateway/

EXPOSE 8000

CMD ["python", "gateway/gateway.py"]