export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface WardrobeItem {
  id: number;
  image_path: string;
  category: string;
  primary_color: string;
  secondary_colors: string[];
  pattern: string;
  description: string;
  classified: boolean;
  upload_source: string;
  created_at: string;
}

export interface WardrobeUploadResult {
  created: WardrobeItem[];
  skipped: string[];
}

export interface Library {
  id: number;
  name: string;
  description: string;
  created_at: string;
  outfit_count: number;
}

export interface Outfit {
  id: number;
  name: string;
  occasion: string;
  color_harmony: string;
  rationale: string;
  library_id: number | null;
  created_at: string;
  items: WardrobeItem[];
}

export interface SuggestedOutfit {
  name: string;
  item_ids: number[];
  color_harmony: string;
  harmony_score: number;
  rationale: string;
}

export interface ColorScheme {
  key: string;
  label: string;
  description: string;
  example_hexes: string[];
}

export interface NamedPalette {
  name: string;
  hexes: string[];
  mood: string;
  best_for: string[];
}
