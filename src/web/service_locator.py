from src.core.features.authentication.interfaces import IAuthenticationService
from src.core.common import exceptions as ex

class ServiceLocator:
    __global_variables = {}
    
    def set_authentication_service(self, service : IAuthenticationService) -> None:
        self.__global_variables["authentication_service"] = service
        
    @property
    def authentication_service(self) -> IAuthenticationService:
        service = self.__global_variables.get("authentication_service")
        if not service:
            raise ex.ServiceDoesNotExistError("There is no Authentication service")
        return service

service_locator = ServiceLocator()