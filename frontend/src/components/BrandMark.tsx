export default function BrandMark({ size = 30 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="brand-mark" aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="#16233F" />
      <path
        d="M16 8.5a2 2 0 1 1 2.2 1.99L16.9 11.7c1.4.1 2.7.7 4.6 2.1l3.7 2.7c.9.66.4 2-.68 2-.24 0-.47-.08-.66-.22L16 13.9 8.14 18.29c-.19.14-.42.22-.66.22-1.08 0-1.58-1.34-.68-2l3.7-2.7c1.9-1.4 3.2-2 4.6-2.1l-1.3-1.2A2 2 0 0 1 16 8.5Z"
        fill="#F6F1E9"
      />
      <rect x="7.5" y="21" width="17" height="2.6" rx="1.3" fill="#F6F1E9" />
    </svg>
  );
}
