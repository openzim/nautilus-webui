from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api import __description__, __titile__, __version__
from api.constants import constants
from api.routes import files, projects, users, utils


def create_app() -> FastAPI:
    app = FastAPI(title=__titile__, description=__description__, version=__version__)

    @app.get("/")
    async def landing() -> RedirectResponse:
        """Redirect to root of latest version of the API"""
        return RedirectResponse(
            f"{constants.api_version_prefix}",
            status_code=HTTPStatus.PERMANENT_REDIRECT,
        )

    api = FastAPI(
        title=__titile__,
        description=__description__,
        version=__version__,
        docs_url="/",
        openapi_tags=[
            {
                "name": "all",
                "description": "all APIs",
            }
        ],
        contact={
            "name": "Kiwix/openZIM Team",
            "url": "https://www.kiwix.org/en/contact/",
            "email": "contact+nautilus_webui@kiwix.org",
        },
        license_info={
            "name": "GNU General Public License v3.0",
            "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
        },
    )
    print(constants.allowed_origins)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=constants.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api.include_router(utils.router)
    api.include_router(users.router)
    projects.router.include_router(files.router)
    api.include_router(projects.router)
    app.mount(constants.api_version_prefix, api)
    return app
