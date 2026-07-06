import { FormEvent, KeyboardEvent, useState } from "react";
import { CornerDownLeft, RefreshCw, Sparkles } from "lucide-react";

type ChatInputProps = {
  disabled?: boolean;
  onSubmit: (message: string) => void;
  onRegenerate: () => void;
};

export function ChatInput({ disabled, onSubmit, onRegenerate }: ChatInputProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    const message = value.trim();
    if (!message || disabled) {
      return;
    }
    onSubmit(message);
    setValue("");
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    submit();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-md border border-border bg-white p-2 shadow-sm dark:bg-slate-950">
      <div className="flex items-start gap-2">
        <div className="mt-2 hidden h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary sm:flex">
          <Sparkles className="h-4 w-4" />
        </div>
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          placeholder="Ask about an asset, incident, procedure, or risk pattern"
          className="max-h-40 min-h-12 flex-1 resize-none border-0 bg-transparent px-2 py-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 dark:text-white"
          disabled={disabled}
        />
        <div className="flex flex-col gap-2">
          <button
            type="submit"
            disabled={disabled || !value.trim()}
            className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-primary text-white disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Send message"
          >
            <CornerDownLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={onRegenerate}
            disabled={disabled}
            className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border text-slate-600 disabled:cursor-not-allowed disabled:opacity-50 dark:text-slate-300"
            aria-label="Regenerate answer"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>
    </form>
  );
}

