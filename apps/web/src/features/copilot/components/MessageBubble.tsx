import { useState } from "react";
import { Check, Clipboard, RotateCcw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils";

import { ConfidenceBadge } from "./ConfidenceBadge";
import { CitationCard } from "./CitationCard";
import { TypingIndicator } from "./LoadingSkeleton";
import type { ChatMessage } from "../types";

type MessageBubbleProps = {
  message: ChatMessage;
  onRegenerate: () => void;
};

export function MessageBubble({ message, onRegenerate }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === "assistant";

  const copy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  };

  return (
    <article className={cn("flex gap-3", !isAssistant && "justify-end")}>
      {isAssistant ? (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary text-sm font-semibold text-white">
          AI
        </div>
      ) : null}
      <div className={cn("max-w-[min(780px,100%)]", !isAssistant && "flex flex-col items-end")}>
        <div
          className={cn(
            "rounded-md border border-border px-4 py-3 shadow-sm",
            isAssistant ? "bg-white dark:bg-slate-950" : "bg-slate-950 text-white dark:bg-slate-100 dark:text-slate-950",
          )}
        >
          {message.status === "streaming" && !message.content ? (
            <TypingIndicator />
          ) : (
            <div className={cn("pm-markdown", !isAssistant && "pm-markdown-invert")}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
        {isAssistant ? (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <ConfidenceBadge confidence={message.confidence} />
            <button
              onClick={copy}
              className="inline-flex h-7 items-center gap-1 rounded-md border border-border px-2 text-xs text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-900"
            >
              {copied ? <Check className="h-3 w-3" /> : <Clipboard className="h-3 w-3" />}
              {copied ? "Copied" : "Copy"}
            </button>
            <button
              onClick={onRegenerate}
              className="inline-flex h-7 items-center gap-1 rounded-md border border-border px-2 text-xs text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-900"
            >
              <RotateCcw className="h-3 w-3" />
              Regenerate
            </button>
          </div>
        ) : null}
        {isAssistant && message.citations?.length ? (
          <div className="mt-3 grid gap-2 md:grid-cols-2">
            {message.citations.slice(0, 2).map((citation, index) => (
              <CitationCard key={`${citation.document_id}-${citation.chunk_id ?? index}`} citation={citation} index={index} />
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}
