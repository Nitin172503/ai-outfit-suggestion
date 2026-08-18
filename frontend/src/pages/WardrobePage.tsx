import { type ChangeEvent, useEffect, useState } from "react";
import { api, ApiError, absoluteUrl } from "../api/client";
import type { WardrobeItem, WardrobeUploadResult } from "../api/types";

const CATEGORIES = ["unknown", "top", "bottom", "dress", "outerwear", "shoes", "accessory", "bag"];

export default function WardrobePage() {
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function refresh() {
    setLoading(true);
    try {
      const data = await api.get<WardrobeItem[]>("/api/wardrobe/");
      setItems(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setUploading(true);
    setError("");
    setNotice("");
    try {
      const form = new FormData();
      form.append("file", file);
      const result = await api.upload<WardrobeUploadResult>("/api/wardrobe/upload", form);
      await refresh();
      const count = result.created.length;
      const skippedNote = result.skipped.length ? ` (${result.skipped.length} skipped)` : "";
      setNotice(`Added ${count} item${count === 1 ? "" : "s"}${skippedNote}.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function updateItem(id: number, patch: Partial<WardrobeItem>) {
    const updated = await api.patch<WardrobeItem>(`/api/wardrobe/${id}`, patch);
    setItems((prev) => prev.map((i) => (i.id === id ? updated : i)));
  }

  async function deleteItem(id: number) {
    await api.delete(`/api/wardrobe/${id}`);
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  const unclassifiedCount = items.filter((i) => i.category === "unknown").length;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Wardrobe</h1>
        <label className="upload-button">
          {uploading ? "Uploading…" : "Upload photo or .zip"}
          <input type="file" accept=".jpg,.jpeg,.png,.zip" onChange={onFileChange} disabled={uploading} hidden />
        </label>
      </div>
      {notice && <div className="form-notice">{notice}</div>}
      {error && <div className="form-error">{error}</div>}
      {!loading && unclassifiedCount > 0 && (
        <div className="form-notice notice-warning">
          {unclassifiedCount} item{unclassifiedCount === 1 ? "" : "s"} still need{unclassifiedCount === 1 ? "s" : ""} a
          category before they show up in suggestions — pick one from the dropdown on each card below.
        </div>
      )}

      {loading ? (
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="empty-state">No items yet. Upload a photo of a garment, or a .zip of several, to get started.</p>
      ) : (
        <div className="grid">
          {items.map((item) => (
            <WardrobeCard
              key={item.id}
              item={item}
              onUpdate={(patch) => updateItem(item.id, patch)}
              onDelete={() => deleteItem(item.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function WardrobeCard({
  item,
  onUpdate,
  onDelete,
}: {
  item: WardrobeItem;
  onUpdate: (patch: Partial<WardrobeItem>) => void;
  onDelete: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [color, setColor] = useState(item.primary_color || "#808080");
  const [description, setDescription] = useState(item.description);

  function saveDetails() {
    onUpdate({ primary_color: color, description });
    setEditing(false);
  }

  return (
    <div className="card">
      <img src={absoluteUrl(item.image_path)} alt={item.description || item.category} />
      <div className="card-body">
        <div className="card-title-row">
          <select
            className={`category-select${item.category === "unknown" ? " unclassified" : ""}`}
            value={item.category}
            onChange={(e) => onUpdate({ category: e.target.value })}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c === "unknown" ? "Set category…" : c}
              </option>
            ))}
          </select>
          {item.primary_color && (
            <span className="swatch" style={{ background: item.primary_color }} title={item.primary_color} />
          )}
        </div>

        {editing ? (
          <div className="edit-form">
            <div className="color-row">
              <input type="color" value={color} onChange={(e) => setColor(e.target.value)} />
              <span>{color}</span>
            </div>
            <input
              type="text"
              placeholder="Short description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <div className="row-buttons">
              <button onClick={saveDetails}>Save</button>
              <button className="secondary" onClick={() => setEditing(false)}>
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <p className="card-desc">{item.description || "No description yet"}</p>
            <div className="row-buttons">
              <button className="secondary" onClick={() => setEditing(true)}>
                Edit details
              </button>
              <button className="danger" onClick={onDelete}>
                Delete
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
