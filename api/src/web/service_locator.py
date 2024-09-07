from api.src.features.authentication.interfaces import IAuthenticationService
from api.src.features.process.interfaces import IProcessService
from api.src.features.process.crud import CRUDRequest
from common import exceptions as ex

class ServiceLocator:
    __global_variables = {}
    
    def set_authentication_service(self, service : IAuthenticationService) -> None:
        self.__global_variables["authentication_service"] = service
        
    def set_process_service(self, service : IProcessService) -> None:
        self.__global_variables["process_service"] = service
        
    def set_crud_request(self, crud : CRUDRequest) -> None:
        self.__global_variables["crud_request"] = crud
        
    @property
    def authentication_service(self) -> IAuthenticationService:
        service = self.__global_variables.get("authentication_service")
        if not service:
            raise ex.ServiceDoesNotExistError("There is no Authentication service")
        return service
    
    @property
    def process_service(self) -> IProcessService:
        service = self.__global_variables.get("process_service")
        if not service:
            raise ex.ServiceDoesNotExistError("There is no Process service")
        return service
    
    @property
    def crud_request(self) -> CRUDRequest:
        crud = self.__global_variables.get("crud_request")
        if not crud:
            raise ex.ServiceDoesNotExistError("There is no CRUD Request")
        return crud

service_locator = ServiceLocator()