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
        service = self.__global_variables.get("authentication_service")
        if not service:
            raise ex.ServiceDoesNotExistError("There is no Authentication service")
        return service
    
    @property
    def request_service(self) -> RequestService:
        service = self.__global_variables.get("request_service")
        if not service:
            raise ex.ServiceDoesNotExistError("There is no Request service")
        return service
    
    @property
    def crud_request(self) -> CRUDRequest:
        crud = self.__global_variables.get("crud_request")
        if not crud:
            raise ex.ServiceDoesNotExistError("There is no CRUD Request")
        return crud

service_locator = ServiceLocator()