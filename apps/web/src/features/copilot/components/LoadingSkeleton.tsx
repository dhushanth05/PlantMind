export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 rounded-md border border-border bg-white px-3 py-2 dark:bg-slate-950">
      {[0, 1, 2].map((index) => (
        <span
          key={index}
          className="h-2 w-2 animate-bounce rounded-full bg-slate-400"
          style={{ animationDelay: `${index * 120}ms` }}
        />
      ))}
    </div>
  );
}

