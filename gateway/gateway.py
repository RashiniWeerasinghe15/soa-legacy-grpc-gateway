import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
from spyne import Application, rpc, ServiceBase, Unicode, Double, Boolean, Integer, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.fault import Fault
from wsgiref.simple_server import make_server

import banking_service_pb2
import banking_service_pb2_grpc

class SoapAccountStatus(ComplexModel):
    __namespace__ = "http://banking.legacy.com/soap"
    account_number = Unicode
    account_holder = Unicode
    status = Unicode
    daily_limit = Double

class SoapRiskResult(ComplexModel):
    __namespace__ = "http://banking.legacy.com/soap"
    evaluation_id = Unicode
    risk_score = Integer
    is_approved = Boolean
    reason = Unicode

class SoapFreezeResult(ComplexModel):
    __namespace__ = "http://banking.legacy.com/soap"
    account_number = Unicode
    is_frozen = Boolean
    timestamp = Unicode

class BankingGatewayService(ServiceBase):

    @staticmethod
    def _handle_grpc_error(e):
        code = e.code()
        details = e.details()
        if code == grpc.StatusCode.INVALID_ARGUMENT:
            raise Fault(faultcode="Client.InvalidArgument", faultstring=details)
        elif code == grpc.StatusCode.NOT_FOUND:
            raise Fault(faultcode="Client.NotFound", faultstring=details)
        else:
            raise Fault(faultcode="Server.InternalError", faultstring=details)

    @rpc(Unicode, _returns=SoapAccountStatus)
    def GetAccountStatus(ctx, account_number):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = banking_service_pb2_grpc.BankingEngineStub(channel)
                res = stub.GetAccountStatus(banking_service_pb2.AccountStatusRequest(account_number=account_number))
                return SoapAccountStatus(
                    account_number=res.account_number,
                    account_holder=res.account_holder,
                    status=res.status,
                    daily_limit=res.daily_limit
                )
        except grpc.RpcError as e:
            BankingGatewayService._handle_grpc_error(e)

    @rpc(Unicode, Double, Unicode, _returns=SoapRiskResult)
    def EvaluateTransactionRisk(ctx, account_number, amount, destination_country):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = banking_service_pb2_grpc.BankingEngineStub(channel)
                res = stub.EvaluateRisk(banking_service_pb2.RiskEvaluationRequest(
                    account_number=account_number,
                    amount=amount,
                    destination_country=destination_country
                ))
                return SoapRiskResult(
                    evaluation_id=res.evaluation_id,
                    risk_score=res.risk_score,
                    is_approved=res.is_approved,
                    reason=res.reason
                )
        except grpc.RpcError as e:
            BankingGatewayService._handle_grpc_error(e)

    @rpc(Unicode, Unicode, _returns=SoapFreezeResult)
    def FreezeAccount(ctx, account_number, reason):
        try:
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = banking_service_pb2_grpc.BankingEngineStub(channel)
                res = stub.FreezeAccount(banking_service_pb2.FreezeAccountRequest(
                    account_number=account_number,
                    reason=reason
                ))
                return SoapFreezeResult(
                    account_number=res.account_number,
                    is_frozen=res.is_frozen,
                    timestamp=res.timestamp
                )
        except grpc.RpcError as e:
            BankingGatewayService._handle_grpc_error(e)

app = Application(
    [BankingGatewayService],
    tns="http://banking.legacy.com/soap",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(app)

if __name__ == "__main__":
    print("[Gateway] Translating Gateway active at http://localhost:8000/?wsdl")
    server = make_server("127.0.0.1", 8000, wsgi_application)
    server.serve_forever()