"use client";
import { useEffect, useRef, useState } from "react";

type Photo = { id: number; filename: string; uploaded_at: string; record_id: number };

export default function PhotoGallery({ trackerKey }: { trackerKey: string }) {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [lightbox, setLightbox] = useState<Photo | null>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`/api/attachments?trackerKey=${encodeURIComponent(trackerKey)}&kind=photo`)
      .then((r) => r.json())
      .then(setPhotos);
  }, [trackerKey]);

  function scrollBy(delta: number) {
    scrollerRef.current?.scrollBy({ left: delta, behavior: "smooth" });
  }

  if (photos.length === 0) return null;

  return (
    <div className="card p-4 mb-6 relative group/gallery">
      <div className="flex items-center gap-2 mb-3">
        <span className="w-1.5 h-1.5 rounded-full bg-purple shadow-[0_0_8px_2px_rgba(139,92,246,0.6)]" />
        <div className="text-sm font-semibold text-white tracking-wide">Photo Gallery — Real Work Evidence ({photos.length})</div>
      </div>

      <button
        onClick={() => scrollBy(-320)}
        className="hidden md:flex absolute left-2 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full items-center justify-center bg-card-2/90 border border-border text-white opacity-0 group-hover/gallery:opacity-100 transition-opacity"
        aria-label="Scroll left"
      >
        ‹
      </button>
      <button
        onClick={() => scrollBy(320)}
        className="hidden md:flex absolute right-2 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full items-center justify-center bg-card-2/90 border border-border text-white opacity-0 group-hover/gallery:opacity-100 transition-opacity"
        aria-label="Scroll right"
      >
        ›
      </button>

      <div
        ref={scrollerRef}
        className="flex gap-3 overflow-x-auto pb-2"
        style={{ scrollSnapType: "x mandatory", scrollBehavior: "smooth" }}
      >
        {photos.map((p) => (
          <button
            key={p.id}
            onClick={() => setLightbox(p)}
            className="shrink-0 w-44 h-32 rounded-lg overflow-hidden border border-border hover:border-teal/50 transition-all hover:scale-[1.03]"
            style={{ scrollSnapAlign: "start" }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={`/api/attachments/${p.id}`} alt={p.filename} className="w-full h-full object-cover" loading="lazy" />
          </button>
        ))}
      </div>

      {lightbox && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/85" onClick={() => setLightbox(null)}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`/api/attachments/${lightbox.id}`} alt={lightbox.filename} className="max-w-full max-h-full rounded-lg shadow-2xl" />
          <button className="absolute top-4 right-4 text-white text-2xl" onClick={() => setLightbox(null)}>✕</button>
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-white/80 text-sm bg-black/50 px-3 py-1 rounded-full">
            {lightbox.filename} · Record #{lightbox.record_id}
          </div>
        </div>
      )}
    </div>
  );
}
