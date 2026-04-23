# Adaptive Skin Intelligence

Personalized skincare recommendations powered by ingredient-level analysis, safety filtering, and explainable AI.

---

## Overview

Adaptive Skin Intelligence is a full-stack web application that generates personalized skincare recommendations based on a user’s skin type, concerns, sensitivities, and ingredient preferences.

Unlike traditional recommenders, this system prioritizes:

* Ingredient-level reasoning
* Safety-first filtering
* Transparent, explainable outputs

The goal is to remove guesswork and help users make informed skincare decisions.

---

## Features

### Personalized Recommendations

* Matches products to user concerns (acne, dryness, dullness, etc.)
* Uses TF-IDF and cosine similarity on ingredient lists

### Safety Engine

* Filters out unsafe products based on:

  * Allergen groups (fragrance, alcohol, essential oils)
  * Pregnancy safety
* Flags:

  * Skin-type incompatibilities
  * Ingredient conflicts

### Explainable Results

Each recommendation includes:

* Why it suits the user
* Key ingredients
* Safety warnings and conflicts

### User Profiling

* Skin type selection
* Multi-select concerns
* Allergen preferences
* Optional pregnancy-safe filtering

---

## Tech Stack

**Backend**

* FastAPI
* Pandas
* Scikit-learn

**Frontend**

* React (Vite)

**Data**

* Ingredient-focused skincare dataset

---

## How It Works

1. User inputs:

   * Skin type
   * Concerns
   * Allergens
   * Preferences

2. System pipeline:

   * Filter unsafe products
   * Filter by skin type
   * Convert ingredient lists into TF-IDF vectors
   * Match against concern-based ingredient queries

3. Output:

   * Ranked product recommendations
   * Explanation (“why”)
   * Safety warnings

---

## Demo

[Watch demo video]https://drive.google.com/file/d/1av3CRwKdnEhqNT3hk5_nlqcn12FXvIAc/view?usp=sharing
---

## Setup

### Backend

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

---

## Current Limitations

* Recommendations can be repetitive due to limited diversification
* Safety labels are currently binary despite warnings
* Dataset size and diversity can be improved
* No persistent feedback loop yet

---

## Future Improvements

**Smarter recommendations**

* Diversity-aware ranking
* Ingredient weighting improvements
* Hybrid scoring (ratings + similarity)

**Safety improvements**

* Multi-tier safety labels (Safe / Caution / Avoid)
* More nuanced conflict handling

**User feedback**

* Store user feedback (“Did this work?”)
* Improve recommendations over time

**Product experience**

* Product images and brand enrichment
* Price normalization
* Routine builder (AM/PM skincare routines)

**Expansion**

* Mobile app version
* Saved user profiles

---

## Vision

This project aims to evolve into a consumer-facing skincare intelligence platform that:

* Personalizes routines at scale
* Educates users about ingredients
* Bridges the gap between dermatology and everyday skincare decisions

---

## License

All rights reserved.

This project is proprietary and may not be used, copied, modified, or distributed without explicit permission from the author.
