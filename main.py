from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal

app = FastAPI(title="GigHub Nairobi Freelance Gigs API - C027-01-0922/2024")

# --- CUSTOM ADMISSION NUMBER CONFIGURATION ---
ALLOWED_CATEGORIES = ["Development", "Design", "Writing"]
CURRENCY = "KES" 

# --- PART 4: PYDANTIC MODELS ---

class GigCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100, description="Title of the gig")
    description: str = Field(..., min_length=20, max_length=500, description="Detailed description")
    category: str = Field(..., description="Job category")
    budget: float = Field(..., gt=0, description="Budget allocation")
    client_name: str = Field(..., min_length=2, max_length=50, description="Name of the client posting")

    @field_validator('category')
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}")
        return value

class GigUpdate(BaseModel):
    budget: Optional[float] = Field(None, gt=0, description="Updated budget amount")
    status: Optional[Literal["Open", "In Progress", "Closed"]] = Field(None, description="Updated gig status")

class GigResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    budget: float
    currency: str
    status: str
    client_name: str


# --- PARTS 1 & 2: INITIAL DATASET (7 Gigs, KES, Dev/Design/Writing) ---
gigs_db = [
    {"id": 1, "title": "Build a React Dashboard", "description": "Build a React dashboard for a fintech startup. Must be responsive and mobile-friendly.", "category": "Development", "budget": 150000.0, "currency": CURRENCY, "status": "Open", "client_name": "Jane Muthoni"},
    {"id": 2, "title": "Mobile App UI/UX Design", "description": "Design high-fidelity wireframes and interactive prototypes for an e-commerce mobile app.", "category": "Design", "budget": 80000.0, "currency": CURRENCY, "status": "Open", "client_name": "John Kamau"},
    {"id": 3, "title": "Technical Blog Writer", "description": "Write five high-quality SEO-optimized technical blog posts about cloud computing trends.", "category": "Writing", "budget": 30000.0, "currency": CURRENCY, "status": "In Progress", "client_name": "Alice Otieno"},
    {"id": 4, "title": "Backend API Integration", "description": "Integrate third-party payment gateways (MPESA Daraja API) into an existing FastAPI backend.", "category": "Development", "budget": 120000.0, "currency": CURRENCY, "status": "Open", "client_name": "David Omwamba"},
    {"id": 5, "title": "Logo and Branding Kit", "description": "Create a modern logo, color palette, and brand identity guidelines for a local logistics company.", "category": "Design", "budget": 45000.0, "currency": CURRENCY, "status": "Closed", "client_name": "Mercy Wanjiku"},
    {"id": 6, "title": "Copywriting for Landing Page", "description": "Craft compelling website copy for a SaaS landing page to improve conversion rates substantially.", "category": "Writing", "budget": 25000.0, "currency": CURRENCY, "status": "Open", "client_name": "Brian Mwangi"},
    {"id": 7, "title": "E-commerce Website Setup", "description": "Set up a fully functional Shopify or WooCommerce store with custom product variations.", "category": "Development", "budget": 200000.0, "currency": CURRENCY, "status": "Open", "client_name": "Sarah Hassan"}
]

next_gig_id = len(gigs_db) + 1


# --- PART 3: API ENDPOINTS ---

@app.get("/gigs", response_model=List[GigResponse])
def get_gigs(
    category: Optional[str] = None,
    min_budget: Optional[float] = Query(None, gt=0),
    max_budget: Optional[float] = Query(None, gt=0)
):
    """Return all gigs with optional filtering by category, min_budget, and max_budget."""
    filtered_gigs = gigs_db
    
    if category:
        filtered_gigs = [g for g in filtered_gigs if g["category"].lower() == category.lower()]
        
    if min_budget is not None:
        filtered_gigs = [g for g in filtered_gigs if g["budget"] >= min_budget]
        
    if max_budget is not None:
        filtered_gigs = [g for g in filtered_gigs if g["budget"] <= max_budget]
        
    return filtered_gigs


@app.get("/gigs/search", response_model=List[GigResponse])
def search_gigs(q: str = Query(..., min_length=1, description="Search query for gig titles")):
    """Search for gigs by title case-insensitively using query parameter 'q'."""
    results = [g for g in gigs_db if q.lower() in g["title"].lower()]
    return results


@app.get("/gigs/{gig_id}", response_model=GigResponse)
def get_gig_by_id(gig_id: int):
    """Return a single gig by its ID. Raises 404 error if not found."""
    for gig in gigs_db:
        if gig["id"] == gig_id:
            return gig
    raise HTTPException(status_code=404, detail=f"Gig with ID {gig_id} not found")


@app.post("/gigs", response_model=GigResponse, status_code=status.HTTP_201_CREATED)
def create_gig(gig_data: GigCreate):
    """Create a new gig with auto-incremented ID, default status 'Open', and KES currency."""
    global next_gig_id
    
    new_gig = {
        "id": next_gig_id,
        "title": gig_data.title,
        "description": gig_data.description,
        "category": gig_data.category,
        "budget": gig_data.budget,
        "currency": CURRENCY,
        "status": "Open",
        "client_name": gig_data.client_name
    }
    
    gigs_db.append(new_gig)
    next_gig_id += 1
    return new_gig


@app.put("/gigs/{gig_id}", response_model=GigResponse)
def update_gig(gig_id: int, update_data: GigUpdate):
    """Update an existing gig's budget and/or status."""
    for gig in gigs_db:
        if gig["id"] == gig_id:
            if update_data.budget is not None:
                gig["budget"] = update_data.budget
            if update_data.status is not None:
                gig["status"] = update_data.status
            return gig
            
    raise HTTPException(status_code=404, detail=f"Gig with ID {gig_id} not found")


@app.delete("/gigs/{gig_id}", status_code=status.HTTP_200_OK)
def delete_gig(gig_id: int):
    """Delete a gig from the database by its ID."""
    global gigs_db
    for index, gig in enumerate(gigs_db):
        if gig["id"] == gig_id:
            gigs_db.pop(index)
            return {"message": f"Gig with ID {gig_id} has been successfully deleted"}
            
    raise HTTPException(status_code=404, detail=f"Gig with ID {gig_id} not found")