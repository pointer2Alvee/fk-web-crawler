from fastapi import FastAPI
from routes import books, changes
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi_pagination import add_pagination

#  Create FastAPI app / ** --> with Swagger UI Documentation
app = FastAPI(
    title="fk-Crawler API",
    description="API to query books and track changes",
    version="1.0.0"
)

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# attach limiter to app state (MUST be done before middleware)
app.state.limiter = limiter

# add SlowAPI middleware 
app.add_middleware(SlowAPIMiddleware)

# add exception handler for rate limit errors
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# include route files to the API "app"
app.include_router(books.router)
app.include_router(changes.router)

#  ** --> Pagination Support
add_pagination(app)
