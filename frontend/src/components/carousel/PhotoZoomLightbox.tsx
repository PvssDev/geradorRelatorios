import React from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

interface PhotoZoomLightboxProps {
  zoomUrl: string | null;
  onClose: () => void;
}

export const PhotoZoomLightbox: React.FC<PhotoZoomLightboxProps> = ({
  zoomUrl,
  onClose,
}) => {
  if (!zoomUrl) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 animate-in fade-in"
      onClick={onClose}
    >
      <div
        className="relative max-h-[90vh] max-w-4xl animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          aria-label="Fechar ampliação"
          onClick={onClose}
          className="absolute -right-3 -top-3 rounded-full bg-white p-2 text-slate-900 shadow-xl hover:scale-110 active:scale-95 transition-all"
        >
          <X className="h-5 w-5" />
        </button>
        <img
          src={zoomUrl}
          alt="Zoom"
          className="max-h-[85vh] rounded-2xl object-contain shadow-2xl ring-1 ring-white/20"
        />
      </div>
    </div>,
    document.body
  );
};

