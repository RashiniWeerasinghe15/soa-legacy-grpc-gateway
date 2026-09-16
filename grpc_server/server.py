import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
from concurrent import futures
import datetime
import banking_service_pb2
import banking_service_pb2_grpc

ACCOUNTS_DB = {
    "ACC-1001": {"holder": "Alice Smith", "status": "ACTIVE", "limit": 5000.0},
    "ACC-1002": {"holder": "Bob Jones", "status": "FROZEN", "limit": 0.0},
}

class BankingEngineServicer(banking_service_pb2_grpc.BankingEngineServicer):

    def GetAccountStatus(self, request, context):
        acc = request.account_number.strip()
        if not acc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Account number cannot be empty.")
        if acc not in ACCOUNTS_DB:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Account {acc} not found.")

        data = ACCOUNTS_DB[acc]
        return banking_service_pb2.AccountStatusResponse(
            account_number=acc,
            account_holder=data["holder"],
            status=data["status"],
            daily_limit=data["limit"]
        )

    def EvaluateRisk(self, request, context):
        if request.amount <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Transaction amount must be greater than zero.")
        if request.account_number not in ACCOUNTS_DB:
            context.abort(grpc.StatusCode.NOT_FOUND, "Account does not exist.")

        is_flagged = request.amount > 10000.0 or request.destination_country.upper() in ["NORTH_KOREA", "SANCTIONED"]
        score = 85 if is_flagged else 15
        
        return banking_service_pb2.RiskEvaluationResponse(
            evaluation_id="EV-88392",
            risk_score=score,
            is_approved=not is_flagged,
            reason="High transaction value or sanctioned destination" if is_flagged else "Approved"
        )

    def FreezeAccount(self, request, context):
        acc = request.account_number.strip()
        if acc not in ACCOUNTS_DB:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Cannot freeze: Account {acc} not found.")

        ACCOUNTS_DB[acc]["status"] = "FROZEN"
        ACCOUNTS_DB[acc]["limit"] = 0.0

        return banking_service_pb2.FreezeAccountResponse(
            account_number=acc,
            is_frozen=True,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    banking_service_pb2_grpc.add_BankingEngineServicer_to_server(BankingEngineServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("[gRPC Server] Running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()