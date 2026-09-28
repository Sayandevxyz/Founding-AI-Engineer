"use client";

import React from "react";
import { CheckCircle2, Loader2, Sparkles, Terminal, AlertCircle } from "lucide-react";

interface AgentProgressProps {
  isOpen: boolean;
  progress: number;
  currentStep: string;
  currentState: string;
  logs: string[];
  errorMessage?: string | null;
  onClose?: () => void;
}

export default function AgentProgressModal({
  isOpen,
  progress,
  currentStep,
  currentState,
  logs,
  errorMessage,
  onClose,
}: AgentProgressProps) {
  if (!isOpen) return null;

  const stages = [
    { id: "DISCOVERING", label: "Browser Discovery & Viewport Capture", threshold: 25 },
    { id: "ANALYZING", label: "Visual & DOM Architectural Analysis", threshold: 40 },
    { id: "EXTRACTING_ASSETS", label: "Asset Extraction & Vector Fallbacks", threshold: 55 },
    { id: "PLANNING", label: "Formulating WebsiteSpec IR Contract", threshold: 65 },
    { id: "GENERATING", label: "Generating Independent React Codebase", threshold: 80 },
    { id: "BUILDING", label: "Build Verification & Runtime Testing", threshold: 90 },
    { id: "READY", label: "Reconstruction Ready & Live Preview", threshold: 100 },
  ];

  const isFailed = currentState === "FAILED" || Boolean(errorMessage);
  const isComplete = currentState === "READY" && progress >= 100;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl rounded-2xl bg-[#0c1220] border border-slate-800 shadow-2xl p-6 md:p-8 space-y-6 ring-1 ring-white/10">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Sparkles className="h-5 w-5 animate-pulse" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">Autonomous Reconstruction Agent</h3>
              <p className="text-xs text-slate-400">Multi-stage pipeline orchestrating Playwright, IR planning & React generation</p>
            </div>
          </div>
          <span className="font-mono text-xl font-extrabold text-blue-400">{progress}%</span>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-medium text-slate-400">
            <span>{currentStep || "Processing..."}</span>
            <span className="font-mono text-slate-300">{currentState}</span>
          </div>
          <div className="w-full h-3 rounded-full bg-slate-900 border border-slate-800 overflow-hidden p-0.5">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                isFailed ? "bg-red-500" : isComplete ? "bg-emerald-500" : "bg-gradient-to-r from-blue-600 via-indigo-500 to-cyan-400"
              }`}
              style={{ width: `${Math.max(5, progress)}%` }}
            />
          </div>
        </div>

        {/* Pipeline Stage Checklist */}
        <div className="space-y-2.5 pt-2">
          {stages.map((st) => {
            const isDone = progress >= st.threshold;
            const isCurrent = currentState === st.id;
            return (
              <div
                key={st.id}
                className={`flex items-center justify-between p-2.5 rounded-lg text-xs transition-colors ${
                  isCurrent
                    ? "bg-blue-600/10 border border-blue-500/30 text-white font-semibold"
                    : isDone
                    ? "bg-slate-900/40 text-slate-300"
                    : "text-slate-500 opacity-60"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  {isDone ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="h-4 w-4 text-blue-400 animate-spin flex-shrink-0" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border border-slate-700 flex-shrink-0" />
                  )}
                  <span>{st.label}</span>
                </div>
                {isCurrent && <span className="text-[10px] text-blue-400 uppercase tracking-wider font-mono">In Progress</span>}
                {isDone && !isCurrent && <span className="text-[10px] text-emerald-400 font-mono">Done</span>}
              </div>
            );
          })}
        </div>

        {/* Terminal Logs Output */}
        <div className="rounded-xl bg-black/60 border border-slate-800/80 p-3 space-y-1.5 font-mono text-[11px] text-slate-400 max-h-36 overflow-y-auto">
          <div className="flex items-center gap-1.5 text-slate-500 text-[10px] border-b border-slate-800 pb-1">
            <Terminal className="h-3 w-3" />
            <span>AGENT TELEMETRY LOGS</span>
          </div>
          {logs.slice(-5).map((line, i) => (
            <p key={i} className="leading-tight text-slate-300">
              <span className="text-blue-500 mr-2">›</span>
              {line}
            </p>
          ))}
          {logs.length === 0 && <p className="text-slate-600 italic">Initializing agent subprocess...</p>}
        </div>

        {/* Error reporting */}
        {isFailed && (
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-start gap-2.5">
            <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Reconstruction issue encountered</p>
              <p className="text-[11px] text-red-400 mt-0.5">{errorMessage || "Unexpected error during autonomous execution."}</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end pt-2">
          {(isComplete || isFailed) && (
            <button
              onClick={onClose}
              className="px-5 py-2 text-sm font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-white transition-all cursor-pointer"
            >
              {isComplete ? "View Generated Project →" : "Close"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
