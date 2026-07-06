const suggestions = [
  "Why is Pump P204 failing repeatedly?",
  "Show previous incidents involving Valve V112.",
  "Which SOP should be followed before maintenance?",
  "Summarize maintenance history of Compressor C301.",
];

export function SuggestionChips({ onSelect }: { onSelect: (question: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((suggestion) => (
        <button
          key={suggestion}
          onClick={() => onSelect(suggestion)}
          className="rounded-full border border-border bg-white px-3 py-1.5 text-sm text-slate-700 transition hover:border-primary hover:bg-slate-50 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-900"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}

