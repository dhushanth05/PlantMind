import { AlertCircle, CheckCircle2, X } from "lucide-react";
import { ReactNode, useCallback, useMemo, useState } from "react";

import { cn } from "@/lib/utils";

import { ToastContext, ToastMessage, ToastTone } from "./toast-context";

export function ToastProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  const dismiss = useCallback((id: string) => {
    setMessages((current) => current.filter((message) => message.id !== id));
  }, []);

  const notify = useCallback(
    (title: string, tone: ToastTone = "info") => {
      const id = crypto.randomUUID();
      setMessages((current) => [{ id, title, tone }, ...current].slice(0, 4));
      window.setTimeout(() => dismiss(id), 5_000);
    },
    [dismiss],
  );

  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 grid w-[min(24rem,calc(100vw-2rem))] gap-2">
        {messages.map((message) => (
          <ToastCard key={message.id} message={message} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastCard({ message, onDismiss }: { message: ToastMessage; onDismiss: (id: string) => void }) {
  const isSuccess = message.tone === "success";
  const Icon = isSuccess ? CheckCircle2 : AlertCircle;

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-md border bg-white p-3 text-sm shadow-lg dark:bg-slate-950",
        isSuccess
          ? "border-emerald-200 text-emerald-800 dark:border-emerald-900 dark:text-emerald-200"
          : message.tone === "error"
            ? "border-red-200 text-red-700 dark:border-red-900 dark:text-red-300"
            : "border-border text-slate-700 dark:text-slate-200",
      )}
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0" />
      <p className="min-w-0 flex-1">{message.title}</p>
      <button type="button" onClick={() => onDismiss(message.id)} className="rounded p-1 hover:bg-slate-100 dark:hover:bg-slate-900">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
