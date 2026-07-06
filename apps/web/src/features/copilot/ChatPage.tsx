import { useEffect, useMemo, useRef } from "react";
import { motion } from "framer-motion";
import { Network, PanelRight, ShieldCheck } from "lucide-react";

import { SectionCard } from "@/components/dashboard/SectionCard";

import { streamChatMessage } from "./api";
import { AssetCard } from "./components/AssetCard";
import { ChatInput } from "./components/ChatInput";
import { CitationCard } from "./components/CitationCard";
import { ConversationSidebar } from "./components/ConversationSidebar";
import { FollowUpCard } from "./components/FollowUpCard";
import { MessageBubble } from "./components/MessageBubble";
import { SuggestionChips } from "./components/SuggestionChips";
import { TypingIndicator } from "./components/LoadingSkeleton";
import { createMessage, useCopilotStore } from "./store";
import type { ChatMessage, GraphContextItem } from "./types";

export function ChatPage() {
  const conversations = useCopilotStore((state) => state.conversations);
  const activeConversationId = useCopilotStore((state) => state.activeConversationId);
  const isStreaming = useCopilotStore((state) => state.isStreaming);
  const setActiveConversation = useCopilotStore((state) => state.setActiveConversation);
  const startConversation = useCopilotStore((state) => state.startConversation);
  const appendMessage = useCopilotStore((state) => state.appendMessage);
  const updateMessage = useCopilotStore((state) => state.updateMessage);
  const clearConversation = useCopilotStore((state) => state.clearConversation);
  const setStreaming = useCopilotStore((state) => state.setStreaming);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const activeConversation = conversations.find((conversation) => conversation.id === activeConversationId) ?? conversations[0];
  const lastAssistant = [...activeConversation.messages].reverse().find((message) => message.role === "assistant");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeConversation.messages]);

  const graphContext = useMemo<GraphContextItem[]>(
    () => [
      { label: "Retrieved chunks", value: String(lastAssistant?.citations?.length ?? 0), tone: "good" },
      { label: "Related assets", value: String(lastAssistant?.relatedAssets?.length ?? 0), tone: "neutral" },
      { label: "Evidence confidence", value: `${Math.round((lastAssistant?.confidence ?? 0) * 100)}%`, tone: "good" },
    ],
    [lastAssistant],
  );

  const submitMessage = async (message: string) => {
    const conversationId = activeConversation.id;
    const userMessage = createMessage("user", message);
    const assistantMessage = createMessage("assistant", "");

    appendMessage(conversationId, userMessage);
    appendMessage(conversationId, assistantMessage);
    setStreaming(true);

    try {
      const response = await streamChatMessage(conversationId, message, (token) => {
        const current = useCopilotStore
          .getState()
          .conversations.find((conversation) => conversation.id === conversationId)
          ?.messages.find((item) => item.id === assistantMessage.id);
        updateMessage(conversationId, assistantMessage.id, { content: `${current?.content ?? ""}${token}` });
      });

      updateMessage(conversationId, assistantMessage.id, {
        content: response.answer,
        confidence: response.confidence,
        citations: response.citations,
        relatedAssets: response.related_assets,
        followUpQuestions: response.follow_up_questions,
        status: "complete",
      });
    } catch (error) {
      updateMessage(conversationId, assistantMessage.id, {
        content:
          "I could not reach the PlantMind Copilot service. Verify the backend is running and try again.",
        confidence: 0,
        citations: [],
        relatedAssets: [],
        followUpQuestions: ["Check backend health for /api/v1/chat."],
        status: "error",
      });
      console.error(error);
    } finally {
      setStreaming(false);
    }
  };

  const regenerate = () => {
    const lastUser = [...activeConversation.messages].reverse().find((message) => message.role === "user");
    if (lastUser && !isStreaming) {
      void submitMessage(lastUser.content);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex gap-4">
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversation.id}
        onSelect={setActiveConversation}
        onNewChat={startConversation}
        onClear={() => clearConversation(activeConversation.id)}
      />

      <section className="flex min-h-[calc(100vh-6rem)] min-w-0 flex-1 flex-col rounded-md border border-border bg-slate-50 dark:bg-slate-950/40">
        <header className="border-b border-border bg-white px-4 py-4 dark:bg-slate-950">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-sm font-medium text-primary">AI Copilot</p>
              <h1 className="mt-1 text-xl font-semibold">Industrial assistant</h1>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                Grounded answers from documents, graph relationships, incidents, procedures, and asset twins.
              </p>
            </div>
            <button
              onClick={startConversation}
              className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-white xl:hidden"
            >
              New Chat
            </button>
          </div>
        </header>

        <div className="flex-1 space-y-5 overflow-y-auto px-4 py-5">
          {activeConversation.messages.length <= 1 ? (
            <div className="mx-auto max-w-3xl rounded-md border border-border bg-white p-5 dark:bg-slate-950">
              <h2 className="text-lg font-semibold">Start an evidence-grounded investigation</h2>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Ask about repeated failures, maintenance history, SOPs, incident patterns, or asset risk.
              </p>
              <div className="mt-4">
                <SuggestionChips onSelect={submitMessage} />
              </div>
            </div>
          ) : null}

          {activeConversation.messages.map((message: ChatMessage) => (
            <MessageBubble key={message.id} message={message} onRegenerate={regenerate} />
          ))}
          {isStreaming ? <TypingIndicator /> : null}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-border bg-white p-4 dark:bg-slate-950">
          <ChatInput disabled={isStreaming} onSubmit={submitMessage} onRegenerate={regenerate} />
        </div>
      </section>

      <aside className="hidden min-h-[calc(100vh-6rem)] w-80 shrink-0 space-y-4 2xl:block">
        <SectionCard title="Citations" description="Expandable evidence returned by PlantMind">
          <div className="space-y-2">
            {lastAssistant?.citations?.length ? (
              lastAssistant.citations.map((citation, index) => (
                <CitationCard key={`${citation.document_id}-${citation.chunk_id ?? index}`} citation={citation} index={index} />
              ))
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">Citations will appear after a grounded response.</p>
            )}
          </div>
        </SectionCard>

        <SectionCard title="Related assets" description="Equipment and asset tags linked to the response">
          <div className="space-y-2">
            {lastAssistant?.relatedAssets?.length ? (
              lastAssistant.relatedAssets.map((asset) => <AssetCard key={asset} asset={asset} />)
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No related assets selected yet.</p>
            )}
          </div>
        </SectionCard>

        <SectionCard title="Graph context" description="Retrieval signals for this answer">
          <div className="space-y-2">
            {graphContext.map((item) => (
              <div key={item.label} className="flex items-center justify-between rounded-md border border-border px-3 py-2">
                <span className="flex items-center gap-2 text-sm">
                  {item.label === "Retrieved chunks" ? <PanelRight className="h-4 w-4 text-primary" /> : null}
                  {item.label === "Related assets" ? <Network className="h-4 w-4 text-primary" /> : null}
                  {item.label === "Evidence confidence" ? <ShieldCheck className="h-4 w-4 text-primary" /> : null}
                  {item.label}
                </span>
                <span className="text-sm font-semibold">{item.value}</span>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Follow-up suggestions">
          <div className="space-y-2">
            {lastAssistant?.followUpQuestions?.length ? (
              lastAssistant.followUpQuestions.map((question) => (
                <FollowUpCard key={question} question={question} onSelect={submitMessage} />
              ))
            ) : (
              <SuggestionChips onSelect={submitMessage} />
            )}
          </div>
        </SectionCard>

        <SectionCard title="Timeline snippets">
          <div className="space-y-3 text-sm">
            <TimelineSnippet title="Inspection" detail="Latest asset evidence appears after retrieval." />
            <TimelineSnippet title="Incident" detail="Incident snippets are linked through citations and graph context." />
            <TimelineSnippet title="Procedure" detail="Relevant SOPs surface in follow-up suggestions." />
          </div>
        </SectionCard>
      </aside>
    </motion.div>
  );
}

function TimelineSnippet({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="border-l-2 border-primary/50 pl-3">
      <p className="font-semibold">{title}</p>
      <p className="mt-1 text-slate-500 dark:text-slate-400">{detail}</p>
    </div>
  );
}
