import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ColorScheme, NamedPalette } from "../api/types";

export default function ColorBookPage() {
  const [schemes, setSchemes] = useState<ColorScheme[]>([]);
  const [palettes, setPalettes] = useState<NamedPalette[]>([]);
  const [checkHexes, setCheckHexes] = useState<string[]>(["#1B2A4A", "#C19A6B"]);
  const [checkResult, setCheckResult] = useState<{ best_match: string; score: number } | null>(null);

  useEffect(() => {
    api.get<ColorScheme[]>("/api/colorbook/schemes").then(setSchemes);
    api.get<NamedPalette[]>("/api/colorbook/palettes").then(setPalettes);
  }, []);

  async function runCheck() {
    const res = await api.post<{ best_match: string; score: number }>("/api/colorbook/check", {
      hexes: checkHexes,
    });
    setCheckResult(res);
  }

  function updateHex(idx: number, value: string) {
    setCheckHexes((prev) => prev.map((h, i) => (i === idx ? value : h)));
  }

  return (
    <div className="page">
      <h1>Color book</h1>
      <p className="subtitle" style={{ marginBottom: "1.75rem" }}>
        The color-wheel rules that power every outfit suggestion.
      </p>

      <section>
        <h2>Try your own combination</h2>
        <div className="color-checker">
          {checkHexes.map((hex, idx) => (
            <input key={idx} type="color" value={hex} onChange={(e) => updateHex(idx, e.target.value)} />
          ))}
          <button className="secondary" onClick={() => setCheckHexes((prev) => [...prev, "#808080"])}>
            + color
          </button>
          {checkHexes.length > 2 && (
            <button className="secondary" onClick={() => setCheckHexes((prev) => prev.slice(0, -1))}>
              - color
            </button>
          )}
          <button onClick={runCheck}>Check harmony</button>
        </div>
        {checkResult && (
          <p className="harmony-tag">
            Best match: <strong>{checkResult.best_match.replace("_", " ")}</strong> (
            {(checkResult.score * 100).toFixed(0)}% fit)
          </p>
        )}
      </section>

      <section>
        <h2>Color-wheel schemes</h2>
        <div className="grid">
          {schemes.map((scheme) => (
            <div className="card" key={scheme.key}>
              <div className="swatch-row">
                {scheme.example_hexes.map((hex) => (
                  <span key={hex} className="swatch large" style={{ background: hex }} />
                ))}
              </div>
              <div className="card-body">
                <h3>{scheme.label}</h3>
                <p className="card-desc">{scheme.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>Curated palettes</h2>
        <div className="grid">
          {palettes.map((p) => (
            <div className="card" key={p.name}>
              <div className="swatch-row">
                {p.hexes.map((hex) => (
                  <span key={hex} className="swatch large" style={{ background: hex }} />
                ))}
              </div>
              <div className="card-body">
                <h3>{p.name}</h3>
                <p className="card-desc">{p.mood}</p>
                <p className="harmony-tag">{p.best_for.join(", ")}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
