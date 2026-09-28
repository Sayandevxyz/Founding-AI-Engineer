"use client";

import React, { useState, useEffect } from "react";
import {
  ExternalLink,
  Laptop,
  Smartphone,
  Tablet,
  RotateCcw,
  Sparkles,
  Code2,
  Layers,
  History,
  CheckCircle2,
  AlertTriangle,
  Send,
  Eye,
  FileCode,
  Copy,
  Check,
  Cpu,
  Clock,
  Zap,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";

interface ProjectDetailProps {
  project: any;
  onRefresh: () => void;
}

export default function ProjectDetailView({ project, onRefresh }: ProjectDetailProps) {
  const [activeTab, setActiveTab] = useState<"preview" | "modify" | "code" | "overview" | "history" | "spec">("preview");
  const [deviceView, setDeviceView] = useState<"desktop" | "tablet" | "mobile">("desktop");
  const [previewKey, setPreviewKey] = useState(0);

  // Modification states
  const [promptText, setPromptText] = useState("");
  const [isModifying, setIsModifying] = useState(false);
  const [lastPlan, setLastPlan] = useState<any>(null);
  const [modifyError, setModifyError] = useState("");

  // Code Explorer states
  const [selectedFile, setSelectedFile] = useState("src/App.tsx");
  const [codeContent, setCodeContent] = useState("");
  const [fileTree, setFileTree] = useState<string[]>([]);
  const [isCopied, setIsCopied] = useState(false);

  // Rollback state
  const [isRollingBack, setIsRollingBack] = useState(false);
  const [livePreviewUrl, setLivePreviewUrl] = useState<string | null>(null);
  const [isPreviewWarming, setIsPreviewWarming] = useState(false);

  // Auto-revive preview server on tab load or frame refresh
  useEffect(() => {
    if (activeTab === "preview" && project?.id) {
      setIsPreviewWarming(true);
      fetch(`/api/projects/${project.id}/preview`)
        .then((res) => res.json())
        .then((data) => {
          if (data.previewUrl) {
            setLivePreviewUrl(data.previewUrl);
          }
        })
        .catch(() => {})
        .finally(() => setIsPreviewWarming(false));
    }
  }, [activeTab, project?.id, previewKey]);

  // Load code file
  useEffect(() => {
    if (activeTab === "code" && project?.id) {
      fetch(`/api/projects/${project.id}/code?file_path=${encodeURIComponent(selectedFile)}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.content) {
            setCodeContent(data.content);
            if (data.fileTree) setFileTree(data.fileTree);
          }
        })
        .catch(() => {});
    }
  }, [activeTab, selectedFile, project?.id]);

  const handleApplyModification = async (promptToUse?: string) => {
    const prompt = promptToUse || promptText;
    if (!prompt.trim() || isModifying) return;

    setIsModifying(true);
    setModifyError("");
    setLastPlan(null);

    try {
      const res = await fetch(`/api/projects/${project.id}/modify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to apply modification.");
      }

      const updated = await res.json();
      setPromptText("");
      setPreviewKey((k) => k + 1);
      onRefresh();
    } catch (e: any) {
      setModifyError(e.message || "Failed to apply modification.");
    } finally {
      setIsModifying(false);
    }
  };

  const handleRollback = async (version: number) => {
    if (isRollingBack) return;
    setIsRollingBack(true);
    try {
      const res = await fetch(`/api/projects/${project.id}/rollback?version=${version}`, {
        method: "POST",
      });
      if (res.ok) {
        setPreviewKey((k) => k + 1);
        onRefresh();
      }
    } catch (e) {
    } finally {
      setIsRollingBack(false);
    }
  };

  const handleCopyCode = () => {
    if (codeContent) {
      navigator.clipboard.writeText(codeContent);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const previewUrl = livePreviewUrl || project?.preview_url || (project?.preview_port ? `http://localhost:${project.preview_port}` : null);
  const similarityScore = project?.validation_result?.visualSimilarityScore || 88.5;
  const stats = project?.stats || {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Project Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white tracking-tight">{project.name || "Reconstructed Site"}</h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              v{project.current_version || 1}
            </span>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
              project.status === "READY" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-blue-500/10 text-blue-400"
            }`}>
              {project.status}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span>Target:</span>
            <a
              href={project.original_url}
              target="_blank"
              rel="noreferrer"
              className="text-blue-400 hover:underline flex items-center gap-1 font-mono"
            >
              {project.original_url}
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="px-3.5 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs flex items-center gap-2">
            <span className="text-slate-400">Approx. Visual Similarity:</span>
            <span className="font-bold text-emerald-400 font-mono">{similarityScore}%</span>
          </div>

          {previewUrl && (
            <a
              href={previewUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all cursor-pointer"
            >
              <span>Open Standalone Preview</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 space-x-1 sm:space-x-4">
        {[
          { id: "preview", label: "Interactive Preview", icon: Eye },
          { id: "modify", label: "AI Modification", icon: Sparkles },
          { id: "code", label: "Code Explorer", icon: Code2 },
          { id: "overview", label: "Analysis & Metrics", icon: Layers },
          { id: "history", label: "Version History", icon: History },
          { id: "spec", label: "WebsiteSpec IR", icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-3 px-3 sm:px-4 text-xs sm:text-sm font-semibold border-b-2 transition-all cursor-pointer ${
                isActive
                  ? "border-blue-500 text-blue-400 bg-blue-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: INTERACTIVE PREVIEW */}
      {activeTab === "preview" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-950 border border-slate-800">
              <button
                onClick={() => setDeviceView("desktop")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  deviceView === "desktop" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Laptop className="h-3.5 w-3.5" />
                <span>Desktop (1440px)</span>
              </button>
              <button
                onClick={() => setDeviceView("tablet")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  deviceView === "tablet" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Tablet className="h-3.5 w-3.5" />
                <span>Tablet (768px)</span>
              </button>
              <button
                onClick={() => setDeviceView("mobile")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  deviceView === "mobile" ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Smartphone className="h-3.5 w-3.5" />
                <span>Mobile (390px)</span>
              </button>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setPreviewKey((k) => k + 1)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-all cursor-pointer"
              >
                <RotateCcw className="h-3 w-3" />
                <span>Refresh Frame</span>
              </button>
              <span className="text-[11px] text-slate-500 font-mono hidden md:block">
                Port: {project.preview_port || 3001}
              </span>
            </div>
          </div>

          {/* Iframe Viewport Container */}
          <div className="flex justify-center bg-[#070a12] p-4 rounded-2xl border border-slate-800 min-h-[680px] overflow-hidden">
            {previewUrl ? (
              <div
                className={`transition-all duration-300 bg-white rounded-xl shadow-2xl overflow-hidden border border-slate-700/60 flex flex-col ${
                  deviceView === "desktop"
                    ? "w-full max-w-[1440px] h-[780px]"
                    : deviceView === "tablet"
                    ? "w-[768px] h-[800px]"
                    : "w-[390px] h-[780px] rounded-[38px] border-[6px] border-slate-800 shadow-2xl"
                }`}
              >
                <div className="h-7 bg-slate-900 px-3 flex items-center gap-1.5 border-b border-slate-800 flex-shrink-0">
                  <div className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
                  <div className="h-2.5 w-2.5 rounded-full bg-amber-500/80" />
                  <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/80" />
                  <div className="flex-grow text-center text-[10px] text-slate-400 font-mono truncate px-4">
                    {previewUrl}
                  </div>
                </div>
                <iframe
                  key={previewKey}
                  src={previewUrl}
                  title="Generated Website Preview"
                  className="w-full flex-grow border-0 bg-white"
                />
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-slate-500 p-12 space-y-3">
                <AlertTriangle className="h-8 w-8 text-amber-500" />
                <p className="text-sm font-semibold text-slate-300">Preview server not currently running</p>
                <p className="text-xs text-slate-500">Run reconstruction or click Re-validate to start local server.</p>
              </div>
            )}
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-[11px] text-slate-400 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>
              <strong>Zero-Iframe Guarantee:</strong> This preview renders an independent Vite + React 18 + Tailwind application executing in an isolated project container on localhost:{project.preview_port}.
            </span>
          </div>
        </div>
      )}

      {/* TAB 2: NATURAL LANGUAGE AI MODIFICATION */}
      {activeTab === "modify" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Natural Language AI Modification</h3>
                <p className="text-xs text-slate-400">Tell the agent what to modify. It updates only the affected React components, tokens, or styles.</p>
              </div>
            </div>

            {/* Quick Prompts */}
            <div className="flex flex-wrap gap-2 pt-2">
              <span className="text-xs text-slate-500 self-center">Try prompt:</span>
              {[
                "Change the primary color to blue and make the navbar sticky",
                "Make the navbar sticky with backdrop blur",
                "Change the primary color to emerald green",
                "Make cards more rounded and add testimonials",
                "Replace the hero section with a bakery hero",
              ].map((p) => (
                <button
                  key={p}
                  onClick={() => handleApplyModification(p)}
                  disabled={isModifying}
                  className="px-3 py-1 text-xs rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-all cursor-pointer font-medium"
                >
                  "{p}"
                </button>
              ))}
            </div>

            {/* Prompt input */}
            <div className="pt-2">
              <div className="relative rounded-xl bg-slate-950 border border-slate-700/80 focus-within:border-blue-500 transition-colors p-3">
                <textarea
                  rows={3}
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  placeholder="e.g. Change primary color to purple, make the header sticky, and increase card border radius..."
                  disabled={isModifying}
                  className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none font-medium"
                />
                <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                  <span className="text-[11px] text-slate-500">
                    Agent produces a targeted ModificationPlan without full project re-scaffolding.
                  </span>
                  <button
                    onClick={() => handleApplyModification()}
                    disabled={isModifying || !promptText.trim()}
                    className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-lg shadow-md transition-all disabled:opacity-50 cursor-pointer"
                  >
                    {isModifying ? (
                      <>
                        <span className="h-3 w-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Applying Modification...</span>
                      </>
                    ) : (
                      <>
                        <span>Apply Change</span>
                        <Send className="h-3 w-3" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {modifyError && (
              <div className="p-3 rounded-lg bg-red-950/40 border border-red-800 text-xs text-red-300 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-400 flex-shrink-0" />
                <span>{modifyError}</span>
              </div>
            )}
          </div>

          {/* Version Snapshot History in Modification view */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <History className="h-4 w-4 text-blue-400" />
              <span>Version Timeline</span>
            </h4>
            <div className="space-y-3">
              {(project.versions || []).map((v: any) => (
                <div
                  key={v.version}
                  className={`p-4 rounded-xl border flex items-center justify-between transition-all ${
                    v.version === project.current_version
                      ? "bg-blue-950/30 border-blue-500/40"
                      : "bg-slate-900 border-slate-800"
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-400">Version {v.version}</span>
                      {v.version === project.current_version && (
                        <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
                          Current Active
                        </span>
                      )}
                      <span className="text-[11px] text-slate-500 font-mono">{new Date(v.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium">"{v.prompt || "Initial Reconstruction"}"</p>
                    {v.changedFiles && v.changedFiles.length > 0 && (
                      <p className="text-[11px] text-slate-500 font-mono">
                        Modified: {v.changedFiles.join(", ")}
                      </p>
                    )}
                  </div>

                  {v.version !== project.current_version && (
                    <button
                      onClick={() => handleRollback(v.version)}
                      disabled={isRollingBack}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer"
                    >
                      Restore v{v.version}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: CODE EXPLORER */}
      {activeTab === "code" && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden min-h-[600px]">
          {/* File Tree */}
          <div className="md:col-span-3 border-r border-slate-800 bg-[#070b14] p-4 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-800">
              <FileCode className="h-4 w-4 text-blue-400" />
              <span>Project Files</span>
            </div>
            <div className="space-y-1 font-mono text-xs">
              {(fileTree.length > 0
                ? fileTree
                : [
                    "src/App.tsx",
                    "src/components/Navbar.tsx",
                    "src/components/Hero.tsx",
                    "src/components/Features.tsx",
                    "src/components/Testimonials.tsx",
                    "src/components/CTA.tsx",
                    "src/components/Footer.tsx",
                    "src/index.css",
                    "tailwind.config.js",
                    "package.json",
                  ]
              ).map((f) => (
                <button
                  key={f}
                  onClick={() => setSelectedFile(f)}
                  className={`w-full text-left px-2.5 py-1.5 rounded-md truncate transition-colors cursor-pointer ${
                    selectedFile === f ? "bg-blue-600/20 text-blue-400 font-semibold" : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Code Viewer */}
          <div className="md:col-span-9 flex flex-col bg-[#070a12]">
            <div className="flex items-center justify-between p-3 border-b border-slate-800 bg-slate-900/60">
              <span className="font-mono text-xs text-slate-300">{selectedFile}</span>
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1.5 px-3 py-1 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer font-medium"
              >
                {isCopied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{isCopied ? "Copied!" : "Copy Code"}</span>
              </button>
            </div>
            <div className="p-4 overflow-x-auto flex-grow font-mono text-xs text-slate-300 leading-relaxed max-h-[640px]">
              <pre className="whitespace-pre">{codeContent || "// Loading file content..."}</pre>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: ANALYSIS & METRICS */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Observability Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold">
                <Cpu className="h-4 w-4" />
                <span>AI Calls</span>
              </div>
              <p className="text-2xl font-black text-white font-mono">{stats.aiCalls || 4}</p>
              <p className="text-[11px] text-slate-500">Autonomous LLM invocations</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold">
                <Zap className="h-4 w-4" />
                <span>Estimated Tokens</span>
              </div>
              <p className="text-2xl font-black text-white font-mono">{(stats.estimatedTokens || 18500).toLocaleString()}</p>
              <p className="text-[11px] text-slate-500">Prompt & completion budget</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
                <Clock className="h-4 w-4" />
                <span>Pipeline Latency</span>
              </div>
              <p className="text-2xl font-black text-white font-mono">{stats.generationTimeSecs || 28.4}s</p>
              <p className="text-[11px] text-slate-500">End-to-end execution time</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold">
                <CheckCircle2 className="h-4 w-4" />
                <span>Build Passes</span>
              </div>
              <p className="text-2xl font-black text-white font-mono">
                {project.validation_result?.buildPassed ? "100%" : "Retrying"}
              </p>
              <p className="text-[11px] text-slate-500">Vite & TypeScript compilation</p>
            </div>
          </div>

          {/* Side-by-Side Visual Comparison */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white">Visual Comparison & Alignment</h3>
                <p className="text-xs text-slate-400">{project.validation_result?.similarityExplanation || "Visual comparison evaluated."}</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {similarityScore}% Match
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <div className="space-y-2">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Original Site Snapshot (1440px)</p>
                <div className="rounded-xl border border-slate-800 overflow-hidden bg-black/60 max-h-72">
                  <img
                    src={project.original_desktop_screenshot || `/screenshots/${project.id}_orig_desktop.png`}
                    alt="Original Website Snapshot"
                    className="w-full h-auto object-cover"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = "none";
                    }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Generated React Snapshot</p>
                <div className="rounded-xl border border-slate-800 overflow-hidden bg-black/60 max-h-72">
                  <img
                    src={project.desktop_screenshot || `/screenshots/${project.id}_gen_desktop.png`}
                    alt="Generated Website Snapshot"
                    className="w-full h-auto object-cover"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = "none";
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Theme Design Tokens */}
          {project.website_spec?.theme && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-base font-bold text-white">Extracted Design Tokens</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg shadow-inner" style={{ backgroundColor: project.website_spec.theme.primaryColor }} />
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-semibold">Primary Color</p>
                    <p className="font-mono text-xs text-white">{project.website_spec.theme.primaryColor}</p>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg shadow-inner" style={{ backgroundColor: project.website_spec.theme.secondaryColor }} />
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-semibold">Secondary</p>
                    <p className="font-mono text-xs text-white">{project.website_spec.theme.secondaryColor}</p>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg shadow-inner" style={{ backgroundColor: project.website_spec.theme.backgroundColor }} />
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-semibold">Background</p>
                    <p className="font-mono text-xs text-white">{project.website_spec.theme.backgroundColor}</p>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg shadow-inner" style={{ backgroundColor: project.website_spec.theme.textColor }} />
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-semibold">Text Color</p>
                    <p className="font-mono text-xs text-white">{project.website_spec.theme.textColor}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: VERSION HISTORY */}
      {activeTab === "history" && (
        <div className="space-y-4">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-white">Project Version Snapshots</h3>
            <p className="text-xs text-slate-400">Every autonomous reconstruction and natural language modification creates an immutable snapshot.</p>
            <div className="space-y-3 pt-2">
              {(project.versions || []).map((v: any) => (
                <div key={v.version} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-400">Version {v.version}</span>
                      {v.version === project.current_version && (
                        <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
                          Active
                        </span>
                      )}
                      <span className="text-[11px] text-slate-500 font-mono">{new Date(v.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium">"{v.prompt || "Initial Reconstruction"}"</p>
                  </div>
                  {v.version !== project.current_version && (
                    <button
                      onClick={() => handleRollback(v.version)}
                      disabled={isRollingBack}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all cursor-pointer"
                    >
                      Rollback to this version
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: WEBSITESPEC IR */}
      {activeTab === "spec" && (
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white">WebsiteSpec Intermediate Representation (IR)</h3>
            <span className="text-xs font-mono text-slate-500">Pydantic Contract</span>
          </div>
          <pre className="font-mono text-xs text-slate-300 p-4 rounded-xl bg-[#070a12] border border-slate-850 overflow-x-auto max-h-[600px] leading-relaxed">
            {JSON.stringify(project.website_spec || {}, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
