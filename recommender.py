# recommender.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from safety_engine import run_safety_check, parse_ingredients

# ── Load & clean data ────────────────────────────────────────────────────────

def load_products(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    print("DEBUG: columns BEFORE cleaning →", df.columns.tolist())
    df.columns = df.columns.str.strip().str.lower()
    print("DEBUG: columns AFTER cleaning →", df.columns.tolist())
    # Rename to standard column names if needed — adjust to match your CSV
    df = df.rename(columns={
    "product_name": "name",
    "product_type": "category",
    "ingredients":  "ingredients",
    "price":        "rating",
})
    df["brand"] = "—"
    df["skin_type"] = "all"

    # Drop rows with no ingredients — useless for recommendations
    df = df.dropna(subset=["ingredients"])
    df = df[df["ingredients"].str.strip() != ""]

    # Lowercase ingredients for consistent matching
    df["ingredients"] = df["ingredients"].str.lower()

    # Fill missing skin_type with "all"
    df["skin_type"] = df["skin_type"].fillna("all").str.lower()

    df = df.reset_index(drop=True)
    return df


# ── TF-IDF ingredient vectors ────────────────────────────────────────────────

def build_tfidf_matrix(df: pd.DataFrame):
    """
    Treat each product's ingredient list as a document.
    Returns the vectorizer and the TF-IDF matrix.
    """
    vectorizer = TfidfVectorizer(
        tokenizer=lambda x: [i.strip() for i in x.split(",")],
        token_pattern=None,
        lowercase=True,
    )
    tfidf_matrix = vectorizer.fit_transform(df["ingredients"])
    return vectorizer, tfidf_matrix


# ── Safety filtering ─────────────────────────────────────────────────────────

def filter_safe_products(df: pd.DataFrame, user_profile: dict) -> pd.DataFrame:
    """Remove products that fail the safety check for this user."""
    def is_safe(row):
        result = run_safety_check(
            {"name": row["name"], "ingredients": row["ingredients"]},
            user_profile
        )
        return result["is_safe"]

    safe_mask = df.apply(is_safe, axis=1)
    return df[safe_mask].reset_index(drop=True)


# ── Skin type filtering ──────────────────────────────────────────────────────

def filter_by_skin_type(df: pd.DataFrame, skin_type: str) -> pd.DataFrame:
    """Keep products tagged for the user's skin type or tagged 'all'."""
    if skin_type == "normal":
        return df
    return df[
        df["skin_type"].str.contains(skin_type, na=False) |
        df["skin_type"].str.contains("all", na=False)
    ].reset_index(drop=True)


# ── User profile → query vector ──────────────────────────────────────────────

def build_user_vector(user_profile: dict, vectorizer: TfidfVectorizer):
    """
    Turn the user's skin concerns into a pseudo ingredient query
    so we can find products that match via cosine similarity.

    concern_ingredient_map maps plain-English concerns to
    key ingredients commonly used to address them.
    """
    concern_ingredient_map = {
        "acne":        "niacinamide, salicylic acid, zinc, benzoyl peroxide",
        "dryness":     "hyaluronic acid, glycerin, ceramide, squalane",
        "dullness":    "vitamin c, ascorbic acid, niacinamide, glycolic acid",
        "aging":       "retinol, peptide, collagen, vitamin c",
        "redness":     "centella asiatica, aloe vera, azelaic acid, green tea",
        "oiliness":    "niacinamide, zinc, clay, salicylic acid",
        "sensitivity": "centella asiatica, aloe vera, ceramide, panthenol",
        "pigmentation":"vitamin c, kojic acid, niacinamide, arbutin",
    }

    concerns = user_profile.get("concerns", [])
    query_ingredients = []
    for concern in concerns:
        mapped = concern_ingredient_map.get(concern.lower(), "")
        if mapped:
            query_ingredients.append(mapped)

    if not query_ingredients:
        # No concerns specified — return None (will rank by rating instead)
        return None

    query_string = ", ".join(query_ingredients)
    return vectorizer.transform([query_string])


# ── Main recommendation function ─────────────────────────────────────────────

def recommend(
    user_profile: dict,
    df: pd.DataFrame,
    tfidf_matrix,
    vectorizer: TfidfVectorizer,
    top_n: int = 5,
    category: str = None,
) -> list[dict]:
    """
    Returns top_n product recommendations for a user.

    user_profile = {
        "skin_type":      "oily",
        "allergen_groups": ["fragrance"],
        "pregnant":       False,
        "concerns":       ["acne", "dullness"],
    }

    Optionally filter by category (e.g. "serum", "moisturizer").
    """

    # Step 1 — safety filter (hard block)
    safe_df = filter_safe_products(df, user_profile)

    # Step 2 — skin type filter
    safe_df = filter_by_skin_type(safe_df, user_profile.get("skin_type", "normal"))

    # Step 3 — optional category filter
    if category:
        safe_df = safe_df[
            safe_df["category"].str.lower().str.contains(category.lower(), na=False)
        ]

    if safe_df.empty:
        return []

    # Step 4 — rebuild TF-IDF on the safe subset only
    safe_vectorizer, safe_matrix = build_tfidf_matrix(safe_df)

    # Step 5 — build user query vector
    user_vector = build_user_vector(user_profile, safe_vectorizer)

    if user_vector is not None:
        # Score by cosine similarity to user's concern ingredients
        scores = cosine_similarity(user_vector, safe_matrix).flatten()
        safe_df = safe_df.copy()
        safe_df["score"] = scores
        safe_df = safe_df.sort_values("score", ascending=False)
    else:
        # No concerns — fall back to rating
        safe_df = safe_df.copy()
        safe_df["score"] = safe_df.get("rating", 0)
        safe_df = safe_df.sort_values("score", ascending=False)

    top = safe_df.head(top_n)

    # Step 6 — build result with explanation
    results = []
    for _, row in top.iterrows():
        safety = run_safety_check(
            {"name": row["name"], "ingredients": row["ingredients"]},
            user_profile
        )
        results.append({
            "name":             row["name"],
            "brand":            row.get("brand", ""),
            "category":         row.get("category", ""),
            "score":            round(float(row["score"]), 3),
            "why":              _build_why(row, user_profile),
            "warnings":         safety["skin_type_warnings"],
            "conflict_warnings": safety["conflict_warnings"],
            "key_ingredients":  _top_ingredients(row["ingredients"]),
        })

    return results


# ── Explanation helpers ──────────────────────────────────────────────────────

def _build_why(row: pd.Series, user_profile: dict) -> str:
    """Generate the 'why it suits you' explanation shown in the UI."""
    reasons = []

    skin_type = user_profile.get("skin_type", "")
    if skin_type and (skin_type in str(row.get("skin_type", "")) or
                      "all" in str(row.get("skin_type", ""))):
        reasons.append(f"suited for {skin_type} skin")

    concerns = user_profile.get("concerns", [])
    concern_keywords = {
        "acne":        ["niacinamide", "salicylic acid", "zinc"],
        "dryness":     ["hyaluronic acid", "glycerin", "ceramide"],
        "dullness":    ["vitamin c", "niacinamide", "glycolic acid"],
        "aging":       ["retinol", "peptide", "vitamin c"],
        "redness":     ["centella asiatica", "aloe vera", "azelaic acid"],
        "pigmentation":["vitamin c", "kojic acid", "niacinamide"],
    }
    ings = row["ingredients"].lower()
    for concern in concerns:
        matched = [k for k in concern_keywords.get(concern, []) if k in ings]
        if matched:
            reasons.append(f"contains {matched[0]} for {concern}")

    if not reasons:
        reasons.append("matches your profile")

    return "Recommended because: " + ", ".join(reasons)


def _top_ingredients(ingredient_string: str, n: int = 5) -> list[str]:
    """Return the first n ingredients (highest concentration = listed first)."""
    parsed = parse_ingredients(ingredient_string)
    return parsed[:n]


# ── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # --- Swap this path for your actual Kaggle CSV ---
    # df = load_products("sephora_products.csv")

    # Demo with a tiny inline dataset so you can run this immediately
    demo_data = {
        "name":        ["Hydra Boost Serum", "Clear Skin Toner", "Glow Serum",
                         "Calming Cream", "Pore Minimizer"],
        "brand":       ["BrandA", "BrandB", "BrandC", "BrandD", "BrandE"],
        "category":    ["serum", "toner", "serum", "moisturizer", "toner"],
        "skin_type":   ["dry", "oily", "all", "sensitive", "oily"],
        "rating":      [4.5, 4.2, 4.8, 4.1, 3.9],
        "ingredients": [
            "water, hyaluronic acid, glycerin, ceramide, panthenol",
            "water, niacinamide, zinc, salicylic acid, witch hazel",
            "water, vitamin c, ascorbic acid, niacinamide, ferulic acid, fragrance",
            "water, centella asiatica, aloe vera, ceramide, squalane",
            "water, niacinamide, zinc, clay, salicylic acid, alcohol denat",
        ]
    }
    df = pd.read_csv("skincare_products.csv")
    vectorizer, tfidf_matrix = build_tfidf_matrix(df)

    user = {
        "skin_type":       "oily",
        "allergen_groups": ["fragrance"],
        "pregnant":        False,
        "concerns":        ["acne", "dullness"],
    }

    print(f"User profile: {user}\n")
    results = recommend(user, df, tfidf_matrix, vectorizer, top_n=3)

    for i, r in enumerate(results, 1):
        print(f"#{i} {r['name']} by {r['brand']} ({r['category']})")
        print(f"    {r['why']}")
        print(f"    Key ingredients: {', '.join(r['key_ingredients'])}")
        if r["warnings"]:
            print(f"    Skin warnings : {r['warnings']}")
        if r["conflict_warnings"]:
            print(f"    Conflicts     : {r['conflict_warnings']}")
        print()