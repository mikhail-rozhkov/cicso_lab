"""Module containing repository of routes."""
import re

from ..controllers import function, health, not_found


class RoutesRepository:
    """Class for routes repository."""
    PATH = 'path'
    METHOD = 'method'
    FACTORY = 'factory'

    def __init__(self):
        """Constructor."""
        self.routes = [
            {
                self.PATH: r'^/api/v1/function$',
                self.METHOD: 'POST',
                self.FACTORY: lambda options, controller=function.FunctionController: controller(options)
            },
            {
                self.PATH: r'^/api/v1/healthcheck$',
                self.METHOD: 'GET',
                self.FACTORY: lambda options, controller=health.HealthController: controller(options)
            },
        ]

    def get_controller(self, method, path, options):
        """Method for getting correct controller for provided route."""
        for route in self.routes:
            if re.match(route[self.PATH], path) and route[self.METHOD] == method:
                return route[self.FACTORY](options)
        return not_found.NotFoundController(options)
