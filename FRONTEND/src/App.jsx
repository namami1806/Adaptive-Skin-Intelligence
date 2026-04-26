import { useState, useEffect } from "react";

const API = "https://adaptive-skin-intelligence.onrender.com";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #faf8f5;
    color: #1a1410;
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    -webkit-font-smoothing: antialiased;
  }

  .serif { font-family: 'DM Serif Display', serif; }

  /* ── Hero ── */
  .hero {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    background: linear-gradient(160deg, #f0e8f0 0%, #e8eef8 30%, #f8ede8 60%, #f5f0e8 100%);
    text-align: center;
  }

  .hero-eyebrow {
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #8a7a6a;
    margin-bottom: 1.5rem;
    font-weight: 500;
  }

  .hero-title {
    font-size: clamp(2.8rem, 7vw, 5rem);
    font-weight: 400;
    line-height: 1.08;
    color: #1a1410;
    max-width: 560px;
    margin-bottom: 1.5rem;
  }

  .hero-title em {
    font-style: italic;
    color: #5a4a7a;
  }

  .hero-sub {
    font-size: 14px;
    color: #8a7a6a;
    line-height: 1.8;
    max-width: 360px;
    margin-bottom: 2.5rem;
  }

  .subscribe-pill {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    border: 0.5px solid rgba(26,20,16,0.2);
    border-radius: 100px;
    padding: 10px 10px 10px 24px;
    font-size: 12px;
    color: #5a5040;
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(8px);
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 3rem;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.5px;
  }
  .subscribe-pill:hover { background: rgba(255,255,255,0.9); }

  .subscribe-arrow {
    width: 30px; height: 30px;
    border-radius: 50%;
    background: #1a1410;
    color: #faf8f5;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
  }

  /* Feature row under hero CTA */
  .features-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    max-width: 500px;
  }

  .feature-chip {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(8px);
    border: 0.5px solid rgba(255,255,255,0.9);
    border-radius: 100px;
    padding: 8px 20px;
  }

  .feature-chip-label {
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
    color: #3a3028;
    margin-bottom: 1px;
  }

  .feature-chip-desc {
    font-size: 10px;
    color: #8a7a6a;
  }

  /* ── Shared page ── */
  .page {
    min-height: 100vh;
    background: linear-gradient(160deg, #f0e8f0 0%, #e8eef8 30%, #f8ede8 60%, #f5f0e8 100%);
    padding: 3rem 1.5rem;
  }

  .page-inner { max-width: 560px; margin: 0 auto; }

  .section-eyebrow {
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #8a7a6a;
    margin-bottom: 14px;
    font-weight: 500;
  }

  .glass-card {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(12px);
    border: 0.5px solid rgba(255,255,255,0.9);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 12px;
  }

  .pill {
    padding: 8px 18px;
    border-radius: 100px;
    font-size: 12px;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all 0.18s;
    font-weight: 400;
    letter-spacing: 0.3px;
    border: none;
  }

  .pill-on  { background: #1a1410; color: #faf8f5; }
  .pill-off {
    background: rgba(255,255,255,0.6);
    color: #5a5040;
    border: 0.5px solid rgba(26,20,16,0.15);
  }
  .pill-off:hover { background: rgba(255,255,255,0.9); border-color: rgba(26,20,16,0.3); }

  .primary-btn {
    width: 100%;
    padding: 15px;
    border-radius: 100px;
    border: none;
    background: #1a1410;
    color: #faf8f5;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 1px;
    cursor: pointer;
    transition: opacity 0.2s;
    margin-top: 8px;
  }
  .primary-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  .primary-btn:hover:not(:disabled) { opacity: 0.82; }

  .ghost-btn {
    background: none; border: none;
    font-size: 11px; letter-spacing: 1.5px;
    text-transform: uppercase; color: #8a7a6a;
    cursor: pointer; font-family: 'Inter', sans-serif;
    transition: color 0.2s;
  }
  .ghost-btn:hover { color: #1a1410; }

  .toggle-track {
    width: 44px; height: 24px; border-radius: 12px;
    border: none; cursor: pointer; position: relative; transition: background 0.2s;
    flex-shrink: 0;
  }
  .toggle-thumb {
    position: absolute; top: 3px;
    width: 18px; height: 18px; border-radius: 50%;
    background: #fff; transition: left 0.2s;
  }

  /* ── Results ── */
  .result-card {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(12px);
    border: 0.5px solid rgba(255,255,255,0.9);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 12px;
    transition: background 0.2s;
  }
  .result-card:hover { background: rgba(255,255,255,0.78); }

  .why-strip {
    background: rgba(90,74,122,0.06);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 10px 0;
  }

  .ing-chip {
    padding: 4px 12px; border-radius: 100px;
    font-size: 11px; background: rgba(26,20,16,0.06);
    color: #3a3028; display: inline-block;
  }

  .safe-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #6aaa7a; display: inline-block; margin-right: 5px;
  }

  .cat-chip {
    padding: 7px 18px; border-radius: 100px;
    font-size: 11px; letter-spacing: 1px;
    font-family: 'Inter', sans-serif; cursor: pointer;
    transition: all 0.18s; font-weight: 400; border: none;
  }
  .cat-on  { background: #1a1410; color: #faf8f5; }
  .cat-off { background: rgba(255,255,255,0.55); color: #8a7a6a; border: 0.5px solid rgba(26,20,16,0.12); }
  .cat-off:hover { background: rgba(255,255,255,0.85); }

  .fb-btn {
    font-size: 11px; padding: 6px 18px; border-radius: 100px;
    font-family: 'Inter', sans-serif; cursor: pointer;
    transition: all 0.18s; background: transparent;
  }
  .fb-yes { border: 0.5px solid rgba(26,20,16,0.2); color: #3a3028; }
  .fb-yes:hover { background: rgba(26,20,16,0.05); }
  .fb-no  { border: 0.5px solid rgba(26,20,16,0.1); color: #8a7a6a; }
  .fb-no:hover  { background: rgba(26,20,16,0.03); }

  .warn   { font-size: 12px; color: #b07040; margin-bottom: 4px; }
  .danger { font-size: 12px; color: #a04040; margin-bottom: 4px; }
`;

// ── Hero ──────────────────────────────────────────────────────────────────

function Hero({ onStart }) {
  const features = [
    { label: "Ingredient matched",  desc: "Science-backed formulas" },
    { label: "Allergen filtered",   desc: "Safe for your sensitivities" },
    { label: "Daily ritual",        desc: "Tailored to your routine" },
    { label: "Instantly curated",   desc: "Results in 60 seconds" },
  ];

  return (
    <div className="hero">
      <p className="hero-eyebrow">Adaptive Skin Intelligence</p>

      <h1 className="serif hero-title">
        The future of<br />skincare is{" "}
        <em>personal</em>
      </h1>

      <p className="hero-sub">
        Personalized recommendations matched to your skin type,
        concerns, and sensitivities — no guesswork, no overwhelm.
      </p>

      <button className="subscribe-pill" onClick={onStart}>
        Begin your skin consultation
        <span className="subscribe-arrow">→</span>
      </button>

      <div className="features-row">
        {features.map(f => (
          <div key={f.label} className="feature-chip">
            <p className="feature-chip-label">{f.label}</p>
            <p className="feature-chip-desc">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Quiz ──────────────────────────────────────────────────────────────────

function SkinQuiz({ onComplete }) {
  const [skinType, setSkinType]   = useState("");
  const [concerns, setConcerns]   = useState([]);
  const [allergens, setAllergens] = useState([]);
  const [pregnant, setPregnant]   = useState(false);
  const [options, setOptions]     = useState({ concerns: [], allergen_groups: [], skin_types: [] });

  useEffect(() => {
    Promise.all([
      fetch(`${API}/concerns`).then(r => r.json()),
      fetch(`${API}/allergen-groups`).then(r => r.json()),
      fetch(`${API}/skin-types`).then(r => r.json()),
    ]).then(([c, a, s]) => setOptions({
      concerns: c.concerns,
      allergen_groups: a.allergen_groups,
      skin_types: s.skin_types,
    }));
  }, []);

  const toggle = (list, set, val) =>
    set(p => p.includes(val) ? p.filter(x => x !== val) : [...p, val]);

  return (
    <div className="page">
      <div className="page-inner">

        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <p className="section-eyebrow">Your consultation</p>
          <h2 className="serif" style={{ fontSize: "clamp(1.8rem,4vw,2.8rem)", fontWeight: 400, lineHeight: 1.15, color: "#000000"}}>
            Tell us about{" "}
            <em style={{ fontStyle: "italic", color: "#5a4a7a" }}>your skin</em>
          </h2>
        </div>

        <div className="glass-card">
          <p className="section-eyebrow">Skin type <span style={{ color: "#a04040" }}>*</span></p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {options.skin_types.map(t => (
              <button key={t} className={`pill ${skinType === t ? "pill-on" : "pill-off"}`}
                onClick={() => setSkinType(t)}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card">
          <p className="section-eyebrow">Skin concerns <span style={{ color: "#8a7a6a", textTransform: "none", letterSpacing: 0, fontSize: 11 }}>— pick all that apply</span></p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {options.concerns.map(c => (
              <button key={c.value} className={`pill ${concerns.includes(c.value) ? "pill-on" : "pill-off"}`}
                onClick={() => toggle(concerns, setConcerns, c.value)}>
                {c.label}
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card">
          <p className="section-eyebrow">Ingredients to avoid <span style={{ color: "#8a7a6a", textTransform: "none", letterSpacing: 0, fontSize: 11 }}>— optional</span></p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {options.allergen_groups.map(a => (
              <button key={a.value} className={`pill ${allergens.includes(a.value) ? "pill-on" : "pill-off"}`}
                onClick={() => toggle(allergens, setAllergens, a.value)}>
                {a.label}
              </button>
            ))}
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16 }}>
            <div>
              <p style={{ fontSize: 13, color: "#1a1410", marginBottom: 3 }}>Pregnancy-safe filter</p>
              <p style={{ fontSize: 12, color: "#8a7a6a" }}>Excludes retinoids, salicylic acid & hydroquinone</p>
            </div>
            <button className="toggle-track"
              style={{ background: pregnant ? "#1a1410" : "rgba(26,20,16,0.12)" }}
              onClick={() => setPregnant(p => !p)}>
              <span className="toggle-thumb" style={{ left: pregnant ? 22 : 3 }} />
            </button>
          </div>
        </div>

        <button className="primary-btn" disabled={!skinType}
          onClick={() => onComplete({ skin_type: skinType, concerns, allergen_groups: allergens, pregnant })}>
          Reveal my recommendations →
        </button>
      </div>
    </div>
  );
}

// ── Results ───────────────────────────────────────────────────────────────

function Results({ profile, onBack }) {
  const [results, setResults]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");
  const [category, setCategory] = useState("");
  const [feedback, setFeedback] = useState({});

  const categories = ["", "serum", "moisturizer", "toner", "cleanser"];

  useEffect(() => {
    setLoading(true); setError("");
    fetch(`${API}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_profile: profile, category: category || null, top_n: 6 }),
    })
      .then(r => { if (!r.ok) throw new Error("No products found. Try adjusting your profile."); return r.json(); })
      .then(d => { setResults(d.results); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [category]);

  return (
    <div className="page">
      <div className="page-inner">

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "2rem" }}>
          <div>
            <p className="section-eyebrow">Your ritual</p>
            <h2 className="serif" style={{ fontSize: "clamp(1.6rem,3.5vw,2.4rem)", fontWeight: 400, lineHeight: 1.15, color: "#000000" }}>
              Curated{" "}
              <em style={{ fontStyle: "italic", color: "#5a4a7a" }}>for you</em>
            </h2>
            <p style={{ fontSize: 12, color: "#8a7a6a", marginTop: 6 }}>
              {profile.skin_type} skin
              {profile.concerns.length > 0 && ` · ${profile.concerns.join(", ")}`}
            </p>
          </div>
          <button className="ghost-btn" onClick={onBack}>← Edit</button>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem", flexWrap: "wrap" }}>
          {categories.map(c => (
            <button key={c} className={`cat-chip ${category === c ? "cat-on" : "cat-off"}`}
              onClick={() => setCategory(c)}>
              {c === "" ? "All" : c.charAt(0).toUpperCase() + c.slice(1)}
            </button>
          ))}
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: "4rem 0" }}>
            <p style={{ fontSize: 13, color: "#8a7a6a", letterSpacing: 1 }}>Curating your products...</p>
          </div>
        )}

        {error && (
          <div className="glass-card">
            <p style={{ color: "#a04040", fontSize: 13 }}>{error}</p>
          </div>
        )}

        {!loading && !error && results.map(r => (
          <div key={r.name} className="result-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
              <div>
                <p className="serif" style={{ fontSize: 17, fontWeight: 400, marginBottom: 2 }}>{r.name}</p>
                <p style={{ fontSize: 12, color: "#8a7a6a" }}>{r.brand} · {r.category}</p>
              </div>
              <span style={{ fontSize: 11, display: "flex", alignItems: "center" }}>
                <span className="safe-dot" />
                <span style={{ color: "#6aaa7a" }}>Safe</span>
              </span>
            </div>

            <div className="why-strip">
              <p style={{ fontSize: 12, color: "#3a3028", lineHeight: 1.7 }}>{r.why}</p>
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, margin: "10px 0" }}>
              {r.key_ingredients.map(ing => (
                <span key={ing} className="ing-chip">{ing}</span>
              ))}
            </div>

            {r.warnings.map(w => <p key={w} className="warn">⚠ {w}</p>)}
            {r.conflict_warnings.map(w => <p key={w} className="danger">⚠ {w}</p>)}

            <div style={{ borderTop: "0.5px solid rgba(26,20,16,0.06)", paddingTop: 10, marginTop: 10, display: "flex", alignItems: "center", gap: 10 }}>
              <p style={{ fontSize: 11, color: "#8a7a6a", letterSpacing: 0.5 }}>Did this work?</p>
              {feedback[r.name] ? (
                <span style={{ fontSize: 11, color: "#6aaa7a" }}>
                  {feedback[r.name] === "yes" ? "Worked for you" : "Noted, we'll improve"}
                </span>
              ) : (
                <div style={{ display: "flex", gap: 6 }}>
                  <button className="fb-btn fb-yes" onClick={() => setFeedback(p => ({ ...p, [r.name]: "yes" }))}>Yes</button>
                  <button className="fb-btn fb-no"  onClick={() => setFeedback(p => ({ ...p, [r.name]: "no" }))}>No</button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Root ──────────────────────────────────────────────────────────────────

export default function App() {
  const [screen, setScreen]   = useState("hero");
  const [profile, setProfile] = useState(null);

  return (
    <>
      <style>{styles}</style>
      {screen === "hero"    && <Hero onStart={() => setScreen("quiz")} />}
      {screen === "quiz"    && <SkinQuiz onComplete={p => { setProfile(p); setScreen("results"); }} />}
      {screen === "results" && <Results profile={profile} onBack={() => setScreen("quiz")} />}
    </>
  );
}