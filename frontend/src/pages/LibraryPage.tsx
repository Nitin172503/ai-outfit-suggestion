import { type FormEvent, useEffect, useState } from "react";
import { api, ApiError, absoluteUrl } from "../api/client";
import type { Library, Outfit } from "../api/types";

export default function LibraryPage() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState("");

  async function refreshLibraries() {
    const data = await api.get<Library[]>("/api/libraries/");
    setLibraries(data);
  }

  useEffect(() => {
    refreshLibraries();
  }, []);

  useEffect(() => {
    const path = selected === null ? "/api/outfits/" : `/api/outfits/?library_id=${selected}`;
    api.get<Outfit[]>(path).then(setOutfits);
  }, [selected]);

  async function createLibrary(e: FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    setError("");
    try {
      await api.post<Library>("/api/libraries/", { name: newName });
      setNewName("");
      await refreshLibraries();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create library");
    }
  }

  async function deleteLibrary(id: number) {
    await api.delete(`/api/libraries/${id}`);
    if (selected === id) setSelected(null);
    await refreshLibraries();
  }

  async function deleteOutfit(id: number) {
    await api.delete(`/api/outfits/${id}`);
    setOutfits((prev) => prev.filter((o) => o.id !== id));
  }

  return (
    <div className="page library-page">
      <aside className="library-sidebar">
        <h2>Libraries</h2>
        <ul className="library-list">
          <li className={selected === null ? "active" : ""} onClick={() => setSelected(null)}>
            All outfits
          </li>
          {libraries.map((lib) => (
            <li key={lib.id} className={selected === lib.id ? "active" : ""}>
              <span onClick={() => setSelected(lib.id)}>
                {lib.name} <em>({lib.outfit_count})</em>
              </span>
              <button className="link-danger" onClick={() => deleteLibrary(lib.id)}>
                ×
              </button>
            </li>
          ))}
        </ul>
        <form className="library-add-form" onSubmit={createLibrary}>
          <input placeholder="New library name" value={newName} onChange={(e) => setNewName(e.target.value)} />
          <button type="submit">Add</button>
        </form>
        {error && <div className="form-error">{error}</div>}
      </aside>

      <div className="library-content">
        <h1>{selected === null ? "All saved outfits" : libraries.find((l) => l.id === selected)?.name}</h1>
        {outfits.length === 0 ? (
          <p className="empty-state">No outfits saved here yet. Save one from Suggestions.</p>
        ) : (
          <div className="grid">
            {outfits.map((outfit) => (
              <div className="card" key={outfit.id}>
                <div className="suggestion-images">
                  {outfit.items.map((item) => (
                    <img key={item.id} src={absoluteUrl(item.image_path)} alt={item.description} />
                  ))}
                </div>
                <div className="card-body">
                  <h3>{outfit.name}</h3>
                  <p className="harmony-tag">
                    {outfit.occasion || "any occasion"} · {outfit.color_harmony.replace("_", " ")}
                  </p>
                  {outfit.rationale && <p className="card-desc">{outfit.rationale}</p>}
                  <div className="row-buttons">
                    <button className="danger" onClick={() => deleteOutfit(outfit.id)}>
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
