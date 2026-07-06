import { MessageSquarePlus, Trash2 } from "lucide-react";

import { cn } from "@/lib/utils";

import type { Conversation } from "../types";

type ConversationSidebarProps = {
  conversations: Conversation[];
  activeConversationId: string;
  onSelect: (conversationId: string) => void;
  onNewChat: () => void;
  onClear: () => void;
};

export function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelect,
  onNewChat,
  onClear,
}: ConversationSidebarProps) {
  return (
    <aside className="hidden min-h-[calc(100vh-6rem)] w-72 shrink-0 rounded-md border border-border bg-white dark:bg-slate-950 xl:block">
      <div className="flex items-center justify-between border-b border-border p-3">
        <div>
          <p className="text-sm font-semibold">Conversations</p>
          <p className="text-xs text-slate-500 dark:text-slate-400">Evidence-grounded sessions</p>
        </div>
        <button
          onClick={onNewChat}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-primary text-white"
          aria-label="New chat"
        >
          <MessageSquarePlus className="h-4 w-4" />
        </button>
      </div>
      <div className="space-y-1 p-2">
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            onClick={() => onSelect(conversation.id)}
            className={cn(
              "w-full rounded-md px-3 py-2 text-left transition hover:bg-slate-100 dark:hover:bg-slate-900",
              conversation.id === activeConversationId && "bg-slate-100 dark:bg-slate-900",
            )}
          >
            <p className="truncate text-sm font-medium">{conversation.title}</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {conversation.messages.length} messages · {new Date(conversation.updatedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          </button>
        ))}
      </div>
      <div className="mt-auto border-t border-border p-3">
        <button
          onClick={onClear}
          className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-md border border-border text-sm font-medium text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-900"
        >
          <Trash2 className="h-4 w-4" />
          Clear conversation
        </button>
      </div>
    </aside>
  );
}

