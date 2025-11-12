# FastAPI Swagger/OpenAPI Documentation Setup
## Complete API Documentation in 30 Minutes

**Effort**: 30 minutes
**Value**: Massive (enables integrations, testing, documentation)
**Status**: Quick win ✅

---

## What You'll Get

- **Interactive API documentation** at `/docs` (Swagger UI)
- **Alternative docs** at `/redoc` (ReDoc)
- **OpenAPI schema** at `/openapi.json`
- **Auto-generated** from your code (no manual writing)
- **Try it out** functionality (test APIs directly in browser)

---

## Step 1: Enable Swagger UI (Already Works!)

FastAPI automatically generates OpenAPI docs. **It's already enabled!**

### Access It Now

```bash
# Start your app
docker-compose up

# Visit in browser:
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
http://localhost:8000/openapi.json  # Raw schema
```

**That's it!** Basic docs already work.

---

## Step 2: Improve Documentation Quality (20 minutes)

### Current State: Basic

```python
# /backend/app/api/providers.py (current)
@router.get("/providers")
async def get_providers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # No description, no examples
    providers = await db.execute(
        select(Provider).offset(skip).limit(limit)
    )
    return providers.scalars().all()
```

**Swagger shows**:
- Endpoint exists
- Parameters: skip, limit
- Returns: unknown

### Enhanced Version:

```python
# /backend/app/api/providers.py (enhanced)
from typing import List
from pydantic import Field

@router.get(
    "/providers",
    response_model=List[ProviderResponse],
    summary="List all providers",
    description="Retrieve a paginated list of all IPTV providers configured in the system.",
    response_description="List of providers with their configuration and status",
    tags=["Providers"]
)
async def get_providers(
    skip: int = Query(0, ge=0, description="Number of providers to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of providers to return"),
    enabled_only: bool = Query(False, description="Filter to show only enabled providers"),
    db: AsyncSession = Depends(get_db)
):
    """
    ## Get Providers

    Retrieve all configured IPTV providers with pagination support.

    ### Parameters:
    - **skip**: Offset for pagination (default: 0)
    - **limit**: Max results per page (default: 100, max: 1000)
    - **enabled_only**: Show only active providers (default: false)

    ### Returns:
    List of providers with:
    - Configuration details
    - Last sync timestamp
    - Active stream counts
    - Health status

    ### Example Response:
    ```json
    [
        {
            "id": 1,
            "name": "Provider A",
            "type": "xstream",
            "enabled": true,
            "total_channels": 1500,
            "active_channels": 1450,
            "last_sync": "2025-01-12T10:30:00Z"
        }
    ]
    ```
    """
    query = select(Provider).offset(skip).limit(limit)

    if enabled_only:
        query = query.where(Provider.enabled == True)

    providers = await db.execute(query)
    return providers.scalars().all()
```

**Swagger now shows**:
- Clear summary and description
- Parameter descriptions and constraints
- Example responses
- Proper tagging for organization

---

## Step 3: Add Response Models (10 minutes)

### Create Pydantic Response Schemas

```python
# /backend/app/schemas/provider.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProviderResponse(BaseModel):
    """Provider response model for API"""

    id: int = Field(..., description="Unique provider ID")
    name: str = Field(..., description="Provider name", example="Premium IPTV")
    type: str = Field(..., description="Provider type", example="xstream")
    enabled: bool = Field(..., description="Whether provider is enabled")
    priority: int = Field(..., description="Provider priority (1-100)", ge=1, le=100)

    # Statistics
    total_channels: int = Field(0, description="Total channels from this provider")
    active_channels: int = Field(0, description="Currently active channels")

    # Timestamps
    last_sync: Optional[datetime] = Field(None, description="Last successful sync")
    last_health_check: Optional[datetime] = Field(None, description="Last health check")

    class Config:
        from_attributes = True  # Allows from ORM models
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Premium IPTV",
                "type": "xstream",
                "enabled": True,
                "priority": 1,
                "total_channels": 1500,
                "active_channels": 1450,
                "last_sync": "2025-01-12T10:30:00Z",
                "last_health_check": "2025-01-12T12:00:00Z"
            }
        }

class ProviderCreate(BaseModel):
    """Schema for creating a new provider"""

    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    type: str = Field(..., description="Provider type (xstream or m3u)")
    enabled: bool = Field(True, description="Enable provider immediately")
    priority: int = Field(1, ge=1, le=100, description="Priority (1=highest)")

    # Xstream fields
    xstream_host: Optional[str] = Field(None, description="Xstream API URL")
    xstream_username: Optional[str] = Field(None, description="Xstream username")
    xstream_password: Optional[str] = Field(None, description="Xstream password")

    # M3U fields
    m3u_url: Optional[str] = Field(None, description="M3U playlist URL")

    # Optional
    epg_url: Optional[str] = Field(None, description="EPG XML URL")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "My IPTV Provider",
                "type": "xstream",
                "enabled": True,
                "priority": 1,
                "xstream_host": "http://example.com:8080",
                "xstream_username": "user",
                "xstream_password": "pass",
                "epg_url": "http://example.com/epg.xml"
            }
        }

class ProviderUpdate(BaseModel):
    """Schema for updating a provider"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=100)
    # ... other optional fields
```

### Use in Endpoints

```python
# /backend/app/api/providers.py
from app.schemas.provider import ProviderResponse, ProviderCreate, ProviderUpdate

@router.get("/providers", response_model=List[ProviderResponse])
async def get_providers(...):
    # ...

@router.post("/providers", response_model=ProviderResponse, status_code=201)
async def create_provider(
    provider: ProviderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new provider"""
    # ...
```

---

## Step 4: Organize with Tags

```python
# /backend/app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="IPTV Stream Manager API",
    description="""
    ## Complete IPTV Management Solution

    Manage IPTV providers, channels, EPG, and VOD content with advanced features:

    * **Providers**: Xstream Codes and M3U playlist support
    * **Channels**: Smart channel merging and quality detection
    * **VOD**: Movies and series with STRM file generation
    * **EPG**: Electronic Program Guide management
    * **Analytics**: Viewing history and statistics
    * **Health**: Automated stream health checking

    ### Authentication
    All endpoints except `/auth/login` require JWT authentication.
    Use the `Authorize` button to set your token.
    """,
    version="1.0.0",
    contact={
        "name": "IPTV Manager Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Login, logout, and token management"
        },
        {
            "name": "Providers",
            "description": "Manage IPTV providers (Xstream, M3U)"
        },
        {
            "name": "Channels",
            "description": "Browse and manage merged channels"
        },
        {
            "name": "VOD",
            "description": "Video on Demand (movies and series)"
        },
        {
            "name": "EPG",
            "description": "Electronic Program Guide management"
        },
        {
            "name": "Analytics",
            "description": "Viewing history and statistics"
        },
        {
            "name": "Settings",
            "description": "Application configuration"
        },
        {
            "name": "Health",
            "description": "Stream health monitoring"
        },
        {
            "name": "System",
            "description": "System information and utilities"
        }
    ]
)

# Then in routers:
router = APIRouter(prefix="/api/providers", tags=["Providers"])
```

---

## Step 5: Add Authentication to Swagger

```python
# /backend/app/main.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

app = FastAPI(
    # ... other config
    openapi_tags=[...],

    # Add security scheme
    swagger_ui_parameters={
        "persistAuthorization": True  # Remember auth between page reloads
    }
)

# Define security scheme in OpenAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add JWT security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token (from /api/auth/login)"
        }
    }

    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Now users can**:
1. Click "Authorize" button in Swagger
2. Enter their JWT token
3. All requests include authentication automatically

---

## Step 6: Add Examples to Endpoints

```python
from fastapi import Body

@router.post("/providers", response_model=ProviderResponse)
async def create_provider(
    provider: ProviderCreate = Body(
        ...,
        example={
            "name": "Premium IPTV",
            "type": "xstream",
            "enabled": True,
            "priority": 1,
            "xstream_host": "http://premium.tv:8080",
            "xstream_username": "demo",
            "xstream_password": "demo123",
            "epg_url": "http://premium.tv/epg.xml"
        }
    ),
    db: AsyncSession = Depends(get_db)
):
    """Create a new IPTV provider"""
    # ...
```

---

## Step 7: Document Error Responses

```python
from fastapi import HTTPException, status

@router.get(
    "/providers/{provider_id}",
    response_model=ProviderResponse,
    responses={
        200: {
            "description": "Provider found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Premium IPTV",
                        "type": "xstream",
                        "enabled": True
                    }
                }
            }
        },
        404: {
            "description": "Provider not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Provider not found"}
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token"
        }
    }
)
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific provider by ID"""

    provider = await db.get(Provider, provider_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return provider
```

---

## Complete Example: Enhanced Endpoint

```python
# /backend/app/api/channels.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.channel import ChannelResponse, ChannelDetail
from app.models.channel import Channel
from sqlalchemy import select

router = APIRouter(prefix="/api/channels", tags=["Channels"])

@router.get(
    "",
    response_model=List[ChannelResponse],
    summary="List all channels",
    description="""
    Retrieve a paginated list of merged channels from all providers.

    Channels are automatically merged across providers based on:
    - Fuzzy name matching (configurable threshold)
    - Region awareness (East/West/Central)
    - Variant detection (HD/4K/Plus)
    - Logo similarity (perceptual hashing)
    """,
    response_description="Paginated list of channels",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "ESPN HD",
                            "category": "Sports",
                            "stream_count": 3,
                            "best_quality": "1080p",
                            "logo_url": "http://example.com/espn.png",
                            "has_epg": True
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid parameters"
        }
    }
)
async def list_channels(
    skip: int = Query(
        0,
        ge=0,
        description="Number of channels to skip for pagination",
        example=0
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of channels to return (1-1000)",
        example=50
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by category (Sports, Movies, News, etc.)",
        example="Sports"
    ),
    enabled: Optional[bool] = Query(
        None,
        description="Filter by enabled status",
        example=True
    ),
    search: Optional[str] = Query(
        None,
        min_length=2,
        description="Search channels by name (min 2 characters)",
        example="ESPN"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    ## List Channels

    Get all merged channels with optional filtering.

    ### Pagination
    Use `skip` and `limit` parameters for pagination:
    - Page 1: skip=0, limit=50
    - Page 2: skip=50, limit=50
    - Page 3: skip=100, limit=50

    ### Filtering
    Multiple filters can be combined:
    - **category**: Show only channels in specific category
    - **enabled**: Show only active/inactive channels
    - **search**: Fuzzy search by channel name

    ### Response
    Each channel includes:
    - Merged channel information
    - Stream count from all providers
    - Best quality available (4K/1080p/720p/SD)
    - EPG availability
    - Logo URL

    ### Performance
    Response time: ~50-200ms for typical queries
    Cached for 5 minutes
    """

    # Build query
    query = select(Channel).offset(skip).limit(limit)

    if category:
        query = query.where(Channel.category == category)

    if enabled is not None:
        query = query.where(Channel.enabled == enabled)

    if search:
        query = query.where(Channel.name.ilike(f"%{search}%"))

    # Execute
    result = await db.execute(query)
    channels = result.scalars().all()

    return channels
```

---

## Accessing Documentation

### Development

```bash
# Swagger UI (interactive)
http://localhost:8000/docs

# ReDoc (clean reading)
http://localhost:8000/redoc

# OpenAPI JSON schema
http://localhost:8000/openapi.json
```

### Production

```bash
# Swagger UI
https://iptv.yourdomain.com/docs

# ReDoc
https://iptv.yourdomain.com/redoc
```

### Disable in Production (Optional)

```python
# /backend/app/main.py
from app.core.config import settings

app = FastAPI(
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)
```

---

## Benefits

### For Developers
- **API reference** always up-to-date
- **Try it out** directly in browser
- **Test endpoints** without Postman
- **Schema validation** automatic

### For Users/Integrators
- **Clear documentation** of all endpoints
- **Example requests/responses**
- **Parameter constraints** visible
- **Easy integration** with third-party tools

### For Testing
- **Manual testing** via Swagger UI
- **Export OpenAPI schema** for automated testing
- **Generate client SDKs** (Python, JavaScript, etc.)

---

## Generate Client SDKs (Bonus)

### Install OpenAPI Generator

```bash
npm install -g @openapitools/openapi-generator-cli
```

### Generate Python Client

```bash
# Download schema
curl http://localhost:8000/openapi.json > openapi.json

# Generate Python client
openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o ./python-client \
  --additional-properties=packageName=iptv_manager_client

# Use client
cd python-client
pip install .
```

```python
# Example usage
from iptv_manager_client import ApiClient, Configuration
from iptv_manager_client.api import ProvidersApi

config = Configuration(host="https://iptv.yourdomain.com")
config.access_token = "your_jwt_token"

with ApiClient(config) as api_client:
    api = ProvidersApi(api_client)
    providers = api.list_providers()
    print(providers)
```

### Generate JavaScript/TypeScript Client

```bash
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o ./typescript-client
```

---

## Testing Swagger Locally

```bash
# 1. Start application
docker-compose up

# 2. Open browser
open http://localhost:8000/docs

# 3. Try authentication
# Click "Authorize" button
# Login via /api/auth/login endpoint
# Copy token from response
# Paste into "Authorize" dialog

# 4. Try endpoints
# Expand any endpoint
# Click "Try it out"
# Fill parameters
# Click "Execute"
# See response
```

---

## Checklist

- [ ] FastAPI app running (`http://localhost:8000/docs` works)
- [ ] Add descriptions to all endpoints
- [ ] Create Pydantic response models
- [ ] Add tags to organize endpoints
- [ ] Configure authentication in Swagger
- [ ] Add examples to request/response
- [ ] Document error responses
- [ ] Test "Try it out" functionality
- [ ] Optionally disable in production

**Total time: 30 minutes for basic setup, 2-3 hours for comprehensive docs**

---

## Result

Before:
- Basic auto-generated docs
- No descriptions
- No examples
- Hard to use

After:
- **Professional API documentation**
- Clear descriptions and examples
- Try-it-out functionality working
- Easy integration for third parties
- Auto-generated client SDKs possible

**All with zero manual documentation writing!** ✅
