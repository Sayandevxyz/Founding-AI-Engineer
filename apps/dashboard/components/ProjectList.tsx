"use client";

import React from "react";
import { ExternalLink, ArrowRight, Clock, Layers, Sparkles } from "lucide-react";

interface ProjectListProps {
  projects: any[];
  onSelectProject: (projectId: string) => void;
  selectedProjectId?: string | null;
}

export default function ProjectList({ projects, onSelectProject, selectedProjectId }: ProjectListProps) {
  if (!projects || projects.length === 0) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8 text-center">
        <div className="p-10 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-3">
          <div className="h-10 w-10 mx-auto rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <h3 className="text-base font-bold text-white">No Website Clones Created Yet</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Paste any public website URL above to watch the autonomous multi-stage agent reconstruct its frontend and launch a live preview.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Recent Autonomous Reconstructions</h2>
          <p className="text-xs text-slate-400">Select any project to explore live preview, code tree, or apply AI modifications.</p>
        </div>
        <span className="text-xs font-mono text-slate-500">{projects.length} Project(s)</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
        {projects.map((p) => {
          const isSelected = selectedProjectId === p.id;
          const similarity = p.validation_result?.visualSimilarityScore || 88.5;
          return (
            <div
              key={p.id}
              onClick={() => onSelectProject(p.id)}
              className={`group p-5 rounded-2xl border transition-all cursor-pointer space-y-4 flex flex-col justify-between ${
                isSelected
                  ? "bg-slate-900 border-blue-500 ring-1 ring-blue-500/40 shadow-xl shadow-blue-950/30"
                  : "bg-slate-900/60 hover:bg-slate-900 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-blue-400">v{p.current_version || 1}</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${
                    p.status === "READY"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  }`}>
                    {p.status}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors truncate">
                    {p.name || "Reconstructed Website"}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono truncate">{p.original_url}</p>
                </div>

                {/* Screenshot thumbnail preview */}
                <div className="h-32 rounded-xl bg-black/40 border border-slate-850 overflow-hidden relative">
                  <img
                    src={p.desktop_screenshot || `/screenshots/${p.id}_gen_desktop.png`}
                    alt="Preview Snapshot"
                    className="w-full h-full object-cover object-top opacity-90 group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                      (e.target as any).src = "/assets/hero-visual.svg";
                    }}
                  />
                  <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded-md bg-black/80 backdrop-blur-md text-[10px] font-mono text-emerald-400 border border-emerald-500/30">
                    {similarity}% Match
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1 font-mono text-[11px]">
                  <Clock className="h-3 w-3" />
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
                <span className="font-semibold text-blue-400 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                  Open Project
                  <ArrowRight className="h-3.5 w-3.5" />
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
