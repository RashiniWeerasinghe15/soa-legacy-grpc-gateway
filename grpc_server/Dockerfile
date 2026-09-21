FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY banking_service_pb2.py .
COPY banking_service_pb2_grpc.py .
COPY grpc_server/ ./grpc_server/

EXPOSE 50051

CMD ["python", "grpc_server/server.py"]