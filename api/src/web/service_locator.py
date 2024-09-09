from api.src.features.authentication.interfaces import IAuthenticationService
from api.src.features.request.service import RequestService
from api.src.features.request.crud import CRUDRequest
from common import exceptions as ex

class ServiceLocator:
    __global_variables = {}
    
    def set_authentication_service(self, service : IAuthenticationService) -> None:
        self.__global_variables["authentication_service"] = service
        
    def set_request_service(self, service : RequestService) -> None:
        self.__global_variables["request_service"] = service
        
    def set_crud_request(self, crud : CRUDRequest) -> None:
        self.__global_variables["crud_request"] = crud
        
    @property
    def authentication_service(self) -> IAuthenticationService:
        try:
            return self.__global_variables["authentication_service"]
        except KeyError:
            raise ex.ServiceDoesNotExistError("Authentication Service Unavailable")
    
    @property
    def request_service(self) -> RequestService:
        try:
            return self.__global_variables["request_service"]
        except KeyError:
            raise ex.ServiceDoesNotExistError("Request Service Unavailable")
    
    @property
    def crud_request(self) -> CRUDRequest:
        try:
            return self.__global_variables["crud_request"]
        except KeyError:
            raise ex.ServiceDoesNotExistError("CRUD Service Unavailable")

service_locator = ServiceLocator()