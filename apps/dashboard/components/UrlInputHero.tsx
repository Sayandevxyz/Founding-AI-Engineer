"use client";

import React, { useState } from "react";
import { Globe, ArrowRight, Shield, Zap, Sparkles, Check, Cpu, Eye, Code } from "lucide-react";

interface UrlInputHeroProps {
  onStartReconstruction: (url: string) => void;
  isLoading: boolean;
}

export default function UrlInputHero({ onStartReconstruction, isLoading }: UrlInputHeroProps) {
  const [inputUrl, setInputUrl] = useState("");
  const [urlError, setUrlError] = useState("");

  const presets = [
    { label: "Supabase (Cloud DB)", url: "https://supabase.com" },
    { label: "Linear (Modern App)", url: "https://linear.app" },
    { label: "Stripe (Fintech)", url: "https://stripe.com" },
    { label: "Example Benchmark", url: "https://example.com" },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUrlError("");

    let url = inputUrl.trim();
    if (!url) {
      setUrlError("Please enter a website URL.");
      return;
    }

    if (url.startsWith("javascript:") || url.startsWith("file:") || url.startsWith("data:")) {
      setUrlError("Invalid URL scheme. Only HTTP and HTTPS are permitted.");
      return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = "https://" + url;
    }

    onStartReconstruction(url);
  };

  const handlePresetClick = (presetUrl: string) => {
    setInputUrl(presetUrl);
    setUrlError("");
    onStartReconstruction(presetUrl);
  };

  return (
    <div className="relative overflow-hidden py-14 md:py-20 border-b border-slate-800/80 bg-gradient-to-b from-[#0e1628] to-[#080c14]">
      {/* Background glow effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[300px] bg-blue-600/10 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-[350px] h-[250px] bg-indigo-500/10 blur-[110px] rounded-full pointer-events-none" />

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 backdrop-blur-md">
          <Sparkles className="h-3.5 w-3.5 text-blue-400 animate-pulse" />
          Autonomous Multi-Stage Engineering Agent
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-white tracking-tight leading-[1.12]">
          Give it a URL. <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-300">Get a working frontend.</span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
          Replicate.AI inspects any public website, extracts DOM & computed styles, captures dual viewports, formulates an IR spec, and generates a standalone React application with Tailwind CSS and natural-language AI editing.
        </p>

        {/* Input Bar Form */}
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto pt-4">
          <div className="relative flex flex-col sm:flex-row items-stretch gap-2.5 p-2 rounded-2xl bg-slate-900/90 border border-slate-700/80 shadow-2xl shadow-blue-950/40 backdrop-blur-xl ring-1 ring-white/10">
            <div className="relative flex-grow flex items-center pl-4">
              <Globe className="h-5 w-5 text-slate-400 mr-3 flex-shrink-0" />
              <input
                type="text"
                value={inputUrl}
                onChange={(e) => {
                  setInputUrl(e.target.value);
                  if (urlError) setUrlError("");
                }}
                placeholder="https://example.com or any public website URL"
                disabled={isLoading}
                className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm sm:text-base focus:outline-none font-medium"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center px-6 py-3.5 text-sm sm:text-base font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-600 hover:from-blue-500 hover:to-indigo-500 rounded-xl shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none flex-shrink-0 gap-2 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Agent Running...</span>
                </>
              ) : (
                <>
                  <span>Clone & Reconstruct</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>

          {urlError && (
            <p className="mt-2 text-xs text-red-400 font-medium text-left pl-4">
              ⚠️ {urlError}
            </p>
          )}

          {/* Quick presets */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-4">
            <span className="text-xs text-slate-500 font-medium mr-1">Quick Demo Presets:</span>
            {presets.map((preset) => (
              <button
                key={preset.url}
                type="button"
                onClick={() => handlePresetClick(preset.url)}
                disabled={isLoading}
                className="px-3 py-1 text-xs rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 hover:border-slate-700 transition-all cursor-pointer font-mono"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </form>

        {/* Core Pillars */}
        <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-1">
            <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold">
              <Eye className="h-4 w-4" />
              <span>Multi-Viewport Playwright</span>
            </div>
            <p className="text-[11px] text-slate-400">Captures 1440px desktop & 390px mobile viewports + computed CSS.</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-1">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold">
              <Cpu className="h-4 w-4" />
              <span>WebsiteSpec IR</span>
            </div>
            <p className="text-[11px] text-slate-400">Strict Pydantic contract between analysis and code generation.</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-1">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
              <Code className="h-4 w-4" />
              <span>Independent React Code</span>
            </div>
            <p className="text-[11px] text-slate-400">Zero iframes. Reusable TypeScript components & Tailwind CSS.</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-1">
            <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold">
              <Zap className="h-4 w-4" />
              <span>Natural Language AI Edit</span>
            </div>
            <p className="text-[11px] text-slate-400">Modify code, theme, and components with version history & rollback.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
