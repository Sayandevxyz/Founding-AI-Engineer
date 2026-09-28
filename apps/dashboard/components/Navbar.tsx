"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, Terminal, Activity, Layers, ShieldCheck, ExternalLink } from "lucide-react";

export default function DashboardNavbar() {
  const [backendHealth, setBackendHealth] = useState<boolean | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setBackendHealth(data.status === "ok"))
      .catch(() => setBackendHealth(false));
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-[#0a0f1d]/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/25 ring-1 ring-white/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg text-white tracking-tight">Replicate<span className="text-blue-500">.AI</span></span>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full">
                  v1.0 Autonomous Agent
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
                Give it a URL. Get a working frontend. Modify it with AI.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
              <span className={`h-2 w-2 rounded-full ${backendHealth ? "bg-emerald-500 animate-pulse" : backendHealth === false ? "bg-red-500" : "bg-amber-500"}`} />
              <span className="text-slate-400">Agent Core:</span>
              <span className="font-mono text-slate-200">{backendHealth ? "Online (Port 8000)" : "Connecting..."}</span>
            </div>

            <div className="flex items-center gap-2 text-xs">
              <span className="px-2.5 py-1 rounded-md bg-slate-800/80 text-slate-300 font-mono border border-slate-700/50 flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                SSRF Guard Active
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
