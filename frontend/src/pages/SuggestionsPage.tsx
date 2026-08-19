import { Fragment, type FormEvent, useEffect, useState } from "react";
import { api, ApiError, absoluteUrl } from "../api/client";
import type { Library, SuggestedOutfit, WardrobeItem } from "../api/types";

export default function SuggestionsPage() {
  const [occasion, setOccasion] = useState("casual");
  const [notes, setNotes] = useState("");
  const [suggestions, setSuggestions] = useState<SuggestedOutfit[]>([]);
  const [wardrobe, setWardrobe] = useState<WardrobeItem[]>([]);
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    api.get<WardrobeItem[]>("/api/wardrobe/").then(setWardrobe);
    api.get<Library[]>("/api/libraries/").then(setLibraries);
  }, []);

  const byId = new Map(wardrobe.map((w) => [w.id, w]));

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    setSuggestions([]);
    try {
      const res = await api.post<{ suggestions: SuggestedOutfit[] }>("/api/outfits/suggest", {
        occasion,
        notes,
      });
      setSuggestions(res.suggestions);
      if (res.suggestions.length === 0) {
        setNotice("No combinations found yet — add a few more classified wardrobe items.");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not generate suggestions");
    } finally {
      setBusy(false);
    }
  }

  async function saveOutfit(s: SuggestedOutfit, libraryId: number | null) {
    await api.post("/api/outfits/", {
      name: s.name,
      occasion,
      item_ids: s.item_ids,
      color_harmony: s.color_harmony,
      rationale: s.rationale,
      library_id: libraryId,
    });
    setNotice(`Saved "${s.name}" to your library.`);
  }

  return (
    <div className="page">
      <h1>Outfit suggestions</h1>
      <p className="subtitle" style={{ marginBottom: "1.25rem" }}>
        Ranked by how well each combination's colors work together.
      </p>
      <form className="inline-form" onSubmit={onSubmit}>
        <label>
          Occasion
          <input value={occasion} onChange={(e) => setOccasion(e.target.value)} placeholder="casual, work, date..." />
        </label>
        <label>
          Notes
          <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="optional" />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? "Thinking…" : "Suggest outfits"}
        </button>
      </form>
      {error && <div className="form-error">{error}</div>}
      {notice && <div className="form-notice">{notice}</div>}

      <div className="suggestion-list">
        {suggestions.map((s, idx) => (
          <SuggestionCard key={idx} suggestion={s} byId={byId} libraries={libraries} onSave={saveOutfit} />
        ))}
      </div>
    </div>
  );
}

function SuggestionCard({
  suggestion,
  byId,
  libraries,
  onSave,
}: {
  suggestion: SuggestedOutfit;
  byId: Map<number, WardrobeItem>;
  libraries: Library[];
  onSave: (s: SuggestedOutfit, libraryId: number | null) => Promise<void>;
}) {
  const [libraryId, setLibraryId] = useState<string>("");
  const [saved, setSaved] = useState(false);

  async function handleSave() {
    await onSave(suggestion, libraryId ? Number(libraryId) : null);
    setSaved(true);
  }

  const items = suggestion.item_ids.map((id) => byId.get(id)).filter((i): i is WardrobeItem => !!i);

  return (
    <div className="suggestion-card">
      <div className="suggestion-images">
        {items.map((item, idx) => (
          <Fragment key={item.id}>
            {idx > 0 && <span className="suggestion-join">+</span>}
            <img src={absoluteUrl(item.image_path)} alt={item.description} />
          </Fragment>
        ))}
      </div>
      <div className="suggestion-body">
        <div className="suggestion-top-row">
          <h3>{suggestion.name}</h3>
          <span className="match-badge">{(suggestion.harmony_score * 100).toFixed(0)}% match</span>
        </div>
        <p className="harmony-tag">{suggestion.color_harmony.replace("_", " ")}</p>
        <p className="suggestion-rationale">{suggestion.rationale}</p>
        <div className="row-buttons">
          <select value={libraryId} onChange={(e) => setLibraryId(e.target.value)}>
            <option value="">No library</option>
            {libraries.map((l) => (
              <option key={l.id} value={l.id}>
                {l.name}
              </option>
            ))}
          </select>
          <button onClick={handleSave} disabled={saved}>
            {saved ? "Saved" : "Save outfit"}
          </button>
        </div>
      </div>
    </div>
  );
}
