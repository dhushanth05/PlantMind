import { Focus, Maximize2, Minus, Plus, RotateCcw } from "lucide-react";

type ToolbarProps = {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onReset: () => void;
  onHighlightPath: () => void;
};

export function Toolbar({ onZoomIn, onZoomOut, onFit, onReset, onHighlightPath }: ToolbarProps) {
  return (
    <div className="absolute left-4 top-4 z-10 flex items-center gap-2 rounded-md border border-border bg-white p-1 shadow-sm dark:bg-slate-950">
      <IconButton label="Zoom in" onClick={onZoomIn} icon={<Plus className="h-4 w-4" />} />
      <IconButton label="Zoom out" onClick={onZoomOut} icon={<Minus className="h-4 w-4" />} />
      <IconButton label="Fit graph" onClick={onFit} icon={<Maximize2 className="h-4 w-4" />} />
      <IconButton label="Highlight neighbors" onClick={onHighlightPath} icon={<Focus className="h-4 w-4" />} />
      <IconButton label="Reset" onClick={onReset} icon={<RotateCcw className="h-4 w-4" />} />
    </div>
  );
}

function IconButton({ label, icon, onClick }: { label: string; icon: React.ReactNode; onClick: () => void }) {
  return (
    <button
      aria-label={label}
      title={label}
      onClick={onClick}
      className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900"
    >
      {icon}
    </button>
  );
}

