import { ArrowUpRight } from "lucide-react";

export function FollowUpCard({ question, onSelect }: { question: string; onSelect: (question: string) => void }) {
  return (
    <button
      onClick={() => onSelect(question)}
      className="flex w-full items-center justify-between gap-3 rounded-md border border-border bg-white px-3 py-2 text-left text-sm text-slate-700 transition hover:border-primary hover:bg-slate-50 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-900"
    >
      <span>{question}</span>
      <ArrowUpRight className="h-4 w-4 shrink-0 text-slate-400" />
    </button>
  );
}

