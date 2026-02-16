from api.routes.layout import register_routes as register_layout_routes
from api.routes.simulate import register_routes as register_simulate_routes
from api.routes.system import register_routes as register_system_routes
from api.routes.tests import register_routes as register_tests_routes

__all__ = [
    "register_layout_routes",
    "register_simulate_routes",
    "register_system_routes",
    "register_tests_routes",
]
