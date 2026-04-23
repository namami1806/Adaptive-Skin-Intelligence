# main.py — FastAPI backend for the skincare recommendation app
#
# Install deps:
#   pip install fastapi uvicorn scikit-learn pandas python-multipart
#
# Run:
#   uvicorn main:app --reload
#
# API will be live at http://localhost:8000
# Docs auto-generated at http://localhost:8000/docs

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd

from recommender import load_products, build_tfidf_matrix, recommend
from safety_engine import run_safety_check

# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Skincare Recommender API",
    description="Personalized skincare recommendations based on skin type, concerns, and allergens.",
    version="1.0.0",
)

# Allow React frontend (localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load data once at startup ────────────────────────────────────────────────
# Swap the demo data below for:
#   df = load_products("sephora_products.csv")

DEMO_DATA = {
    "name":        ["Hydra Boost Serum", "Clear Skin Toner", "Glow Serum",
                    "Calming Cream", "Pore Minimizer", "Barrier Repair Moisturizer",
                    "Vitamin C Brightening Serum", "Gentle Foaming Cleanser"],
    "brand":       ["BrandA", "BrandB", "BrandC", "BrandD", "BrandE",
                    "BrandF", "BrandG", "BrandH"],
    "category":    ["serum", "toner", "serum", "moisturizer", "toner",
                    "moisturizer", "serum", "cleanser"],
    "skin_type":   ["dry", "oily", "all", "sensitive", "oily",
                    "dry,sensitive", "all", "all"],
    "rating":      [4.5, 4.2, 4.8, 4.1, 3.9, 4.6, 4.7, 4.3],
    "ingredients": [
        "water, hyaluronic acid, glycerin, ceramide, panthenol",
        "water, niacinamide, zinc, salicylic acid, witch hazel",
        "water, vitamin c, ascorbic acid, niacinamide, ferulic acid, fragrance",
        "water, centella asiatica, aloe vera, ceramide, squalane",
        "water, niacinamide, zinc, clay, salicylic acid, alcohol denat",
        "water, ceramide, squalane, glycerin, cholesterol, fatty acids",
        "water, vitamin c, ascorbic acid, ferulic acid, vitamin e, glycerin",
        "water, glycerin, panthenol, aloe vera, sodium lauryl sulfate",
    ]
}

df = load_products("skincare_products.csv")
vectorizer, tfidf_matrix = build_tfidf_matrix(df)

# ── Request / Response models ────────────────────────────────────────────────

class UserProfile(BaseModel):
    skin_type: str = Field(
        ...,
        description="User's skin type",
        examples=["oily", "dry", "combination", "sensitive", "normal"]
    )
    concerns: list[str] = Field(
        default=[],
        description="Skin concerns to address",
        examples=[["acne", "dullness"]]
    )
    allergen_groups: list[str] = Field(
        default=[],
        description="Allergen groups to avoid",
        examples=[["fragrance", "essential_oils"]]
    )
    pregnant: bool = Field(
        default=False,
        description="Whether to apply pregnancy safety filter"
    )

class RecommendRequest(BaseModel):
    user_profile: UserProfile
    category: Optional[str] = Field(
        default=None,
        description="Filter by product category (e.g. serum, moisturizer)",
        examples=["serum"]
    )
    top_n: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of recommendations to return"
    )

class SafetyCheckRequest(BaseModel):
    product_name: str
    ingredients: str
    user_profile: UserProfile

class ProductResult(BaseModel):
    name: str
    brand: str
    category: str
    score: float
    why: str
    key_ingredients: list[str]
    warnings: list[str]
    conflict_warnings: list[str]

class RecommendResponse(BaseModel):
    results: list[ProductResult]
    total_safe_products: int
    filters_applied: dict

class SafetyResponse(BaseModel):
    product: str
    is_safe: bool
    summary: str
    allergen_flags: list[str]
    pregnancy_flags: list[str]
    skin_type_warnings: list[str]
    conflict_warnings: list[str]

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Skincare Recommender API is running",
        "docs": "/docs",
        "endpoints": ["/recommend", "/safety-check", "/products", "/skin-types", "/concerns"]
    }


@app.post("/recommend", response_model=RecommendResponse)
def get_recommendations(request: RecommendRequest):
    """
    Get personalized product recommendations for a user profile.
    Products are safety-filtered first, then ranked by ingredient
    similarity to the user's skin concerns.
    """
    profile = request.user_profile.model_dump()

    results = recommend(
        user_profile=profile,
        df=df,
        tfidf_matrix=tfidf_matrix,
        vectorizer=vectorizer,
        top_n=request.top_n,
        category=request.category,
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No safe products found matching your profile. Try adjusting your filters."
        )

    # Count how many products passed safety filter
    from recommender import filter_safe_products, filter_by_skin_type
    safe_df = filter_safe_products(df, profile)
    safe_df = filter_by_skin_type(safe_df, profile.get("skin_type", "normal"))

    return RecommendResponse(
        results=[ProductResult(**r) for r in results],
        total_safe_products=len(safe_df),
        filters_applied={
            "skin_type": profile.get("skin_type"),
            "allergen_groups": profile.get("allergen_groups", []),
            "pregnant": profile.get("pregnant", False),
            "category": request.category,
        }
    )


@app.post("/safety-check", response_model=SafetyResponse)
def safety_check(request: SafetyCheckRequest):
    """
    Run a safety check on a single product for a given user profile.
    Useful for checking products the user already owns.
    """
    result = run_safety_check(
        product={"name": request.product_name, "ingredients": request.ingredients},
        user_profile=request.user_profile.model_dump(),
    )
    return SafetyResponse(**result)


@app.get("/products")
def list_products(category: Optional[str] = None, skin_type: Optional[str] = None):
    """Browse all products, optionally filtered by category or skin type."""
    filtered = df.copy()
    if category:
        filtered = filtered[filtered["category"].str.contains(category, case=False, na=False)]
    if skin_type:
        filtered = filtered[
            filtered["skin_type"].str.contains(skin_type, case=False, na=False) |
            filtered["skin_type"].str.contains("all", case=False, na=False)
        ]
    return {
        "total": len(filtered),
        "products": filtered[["name", "brand", "category", "skin_type", "rating"]]
                    .to_dict(orient="records")
    }


@app.get("/skin-types")
def get_skin_types():
    """Return valid skin type options for the frontend form."""
    return {
        "skin_types": ["oily", "dry", "combination", "sensitive", "normal"]
    }


@app.get("/concerns")
def get_concerns():
    """Return valid concern options for the frontend form."""
    return {
        "concerns": [
            {"value": "acne",         "label": "Acne & breakouts"},
            {"value": "dryness",      "label": "Dryness & dehydration"},
            {"value": "dullness",     "label": "Dullness & uneven tone"},
            {"value": "aging",        "label": "Fine lines & aging"},
            {"value": "redness",      "label": "Redness & irritation"},
            {"value": "oiliness",     "label": "Excess oil & shine"},
            {"value": "sensitivity",  "label": "Sensitivity"},
            {"value": "pigmentation", "label": "Dark spots & pigmentation"},
        ]
    }


@app.get("/allergen-groups")
def get_allergen_groups():
    """Return valid allergen groups for the frontend form."""
    return {
        "allergen_groups": [
            {"value": "fragrance",     "label": "Fragrance & parfum"},
            {"value": "essential_oils","label": "Essential oils"},
            {"value": "preservatives", "label": "Preservatives (MI, formaldehyde)"},
            {"value": "alcohol",       "label": "Alcohol"},
        ]
    }