# safety_engine.py

ALLERGEN_GROUPS = {
    "fragrance": [
        "fragrance", "parfum", "linalool", "limonene", "citronellol",
        "geraniol", "eugenol", "cinnamal", "benzyl alcohol"
    ],
    "essential_oils": [
        "tea tree oil", "lavender oil", "peppermint oil", "eucalyptus oil",
        "rose oil", "jasmine oil"
    ],
    "preservatives": [
        "methylisothiazolinone", "methylchloroisothiazolinone",
        "formaldehyde", "quaternium-15", "dmdm hydantoin",
        "imidazolidinyl urea"
    ],
    "alcohol": [
        "alcohol denat", "denatured alcohol", "sd alcohol", "ethanol"
    ],
}

PREGNANCY_AVOID = [
    "retinol", "retinyl palmitate", "retinoic acid", "tretinoin",
    "salicylic acid", "hydroquinone", "formaldehyde",
    "dihydroxyacetone", "benzoyl peroxide",
]

SKIN_TYPE_AVOID = {
    "oily": [
        "mineral oil", "petrolatum", "coconut oil", "isopropyl myristate",
        "lanolin"
    ],
    "dry": [
        "alcohol denat", "sd alcohol", "denatured alcohol"
    ],
    "sensitive": [
        "fragrance", "parfum", "alcohol denat", "menthol",
        "methylisothiazolinone", "sodium lauryl sulfate"
    ],
}

CONFLICT_PAIRS = [
    (["retinol", "retinoic acid"], ["aha", "glycolic acid", "lactic acid",
                                     "salicylic acid", "bha"]),
    (["vitamin c", "ascorbic acid"], ["niacinamide"]),
    (["benzoyl peroxide"], ["retinol", "retinoic acid"]),
]


def parse_ingredients(ingredient_string: str) -> list[str]:
    """Convert raw ingredient string to a clean lowercase list."""
    return [i.strip().lower() for i in ingredient_string.split(",") if i.strip()]


def check_allergens(ingredients: list[str], user_allergen_groups: list[str]) -> list[str]:
    """
    Returns a list of flagged ingredients based on the user's
    selected allergen groups (e.g. ['fragrance', 'essential_oils']).
    """
    flagged = []
    for group in user_allergen_groups:
        allergens = ALLERGEN_GROUPS.get(group, [])
        for allergen in allergens:
            if any(allergen in ing for ing in ingredients):
                flagged.append(allergen)
    return flagged


def check_pregnancy(ingredients: list[str]) -> list[str]:
    """Returns any pregnancy-unsafe ingredients found in the product."""
    return [ing for ing in PREGNANCY_AVOID
            if any(ing in product_ing for product_ing in ingredients)]


def check_skin_type(ingredients: list[str], skin_type: str) -> list[str]:
    """Returns ingredients that are generally not recommended for the user's skin type."""
    avoid_list = SKIN_TYPE_AVOID.get(skin_type, [])
    return [ing for ing in avoid_list
            if any(ing in product_ing for product_ing in ingredients)]


def check_conflicts(routine_products: list[dict]) -> list[str]:
    """
    Given a list of products the user is using together,
    returns warnings about conflicting ingredient combinations.
    Each product is a dict with at least an 'ingredients' key (list of str).
    """
    all_ingredients = []
    for product in routine_products:
        all_ingredients.extend(product.get("ingredients", []))

    warnings = []
    for group_a, group_b in CONFLICT_PAIRS:
        has_a = any(a in ing for ing in all_ingredients for a in group_a)
        has_b = any(b in ing for ing in all_ingredients for b in group_b)
        if has_a and has_b:
            warnings.append(
                f"Potential conflict: {', '.join(group_a)} + {', '.join(group_b)} "
                f"— consider using these at different times (AM/PM)."
            )
    return warnings


def run_safety_check(
    product: dict,
    user_profile: dict,
    routine_products: list[dict] = None
) -> dict:
    """
    Master function. Pass in a product and user profile, get back a
    safety report.

    product = {
        "name": "Some Serum",
        "ingredients": "Niacinamide, Retinol, Fragrance, Water, ..."
    }

    user_profile = {
        "skin_type": "sensitive",        # oily | dry | combination | sensitive | normal
        "allergen_groups": ["fragrance"], # list of keys from ALLERGEN_GROUPS
        "pregnant": False
    }
    """
    ingredients = parse_ingredients(product["ingredients"])

    allergen_flags = check_allergens(ingredients, user_profile.get("allergen_groups", []))
    pregnancy_flags = check_pregnancy(ingredients) if user_profile.get("pregnant") else []
    skin_type_flags = check_skin_type(ingredients, user_profile.get("skin_type", "normal"))
    conflict_warnings = check_conflicts(routine_products or [{"ingredients": ingredients}])

    is_safe = not allergen_flags and not pregnancy_flags

    return {
        "product": product["name"],
        "is_safe": is_safe,
        "allergen_flags": allergen_flags,
        "pregnancy_flags": pregnancy_flags,
        "skin_type_warnings": skin_type_flags,
        "conflict_warnings": conflict_warnings,
        "summary": _build_summary(is_safe, allergen_flags, pregnancy_flags,
                                   skin_type_flags, conflict_warnings)
    }


def _build_summary(is_safe, allergen_flags, pregnancy_flags,
                   skin_type_flags, conflict_warnings) -> str:
    if is_safe and not skin_type_flags and not conflict_warnings:
        return "No issues found."
    parts = []
    if allergen_flags:
        parts.append(f"Contains allergens: {', '.join(allergen_flags)}")
    if pregnancy_flags:
        parts.append(f"Avoid during pregnancy: {', '.join(pregnancy_flags)}")
    if skin_type_flags:
        parts.append(f"May not suit your skin type: {', '.join(skin_type_flags)}")
    if conflict_warnings:
        parts.extend(conflict_warnings)
    return " | ".join(parts)


# ── Quick demo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    product = {
        "name": "Glow Serum X",
        "ingredients": "Water, Niacinamide, Retinol, Fragrance, Glycolic Acid, Linalool"
    }

    user = {
        "skin_type": "sensitive",
        "allergen_groups": ["fragrance"],
        "pregnant": False
    }

    result = run_safety_check(product, user)

    print(f"Product : {result['product']}")
    print(f"Safe    : {result['is_safe']}")
    print(f"Summary : {result['summary']}")
    print()
    if result["allergen_flags"]:
        print(f"Allergens        : {result['allergen_flags']}")
    if result["skin_type_warnings"]:
        print(f"Skin type issues : {result['skin_type_warnings']}")
    if result["conflict_warnings"]:
        print(f"Conflicts        : {result['conflict_warnings']}")