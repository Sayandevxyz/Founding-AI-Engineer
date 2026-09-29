"use client";

import React, { useState, useEffect } from "react";
import DashboardNavbar from "@/components/Navbar";
import UrlInputHero from "@/components/UrlInputHero";
import AgentProgressModal from "@/components/AgentProgressModal";
import ProjectDetailView from "@/components/ProjectDetailView";
import ProjectList from "@/components/ProjectList";

export default function DashboardPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [activeProject, setActiveProject] = useState<any | null>(null);

  // Agent Progress States
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [currentState, setCurrentState] = useState("INITIALIZED");
  const [logs, setLogs] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch projects on load
  const loadProjects = async () => {
    try {
      const res = await fetch("/api/projects");
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0 && !selectedProjectId) {
          const readyProj = data.find((p: any) => p.status === "READY") || data[0];
          setSelectedProjectId(readyProj.id);
          setActiveProject(readyProj);
        }
      }
    } catch (e) {
      // Backend might still be starting
    }
  };

  useEffect(() => {
    loadProjects();
    const interval = setInterval(loadProjects, 10000);
    return () => clearInterval(interval);
  }, []);

  // Update activeProject when selectedProjectId changes
  useEffect(() => {
    if (selectedProjectId) {
      fetch(`/api/projects/${selectedProjectId}`)
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data) setActiveProject(data);
        })
        .catch(() => {});
    }
  }, [selectedProjectId]);

async function getErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (data?.detail) return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    if (data?.message) return data.message;
    if (data?.error) return data.error;
  } catch {
    try {
      const text = await res.text();
      if (text.includes("Internal Server Error") || res.status === 500) {
        return `Backend server error (${res.status} Internal Server Error). Please make sure the FastAPI backend is running on http://127.0.0.1:8000 (run 'npm run dev' or 'npm run dev:backend').`;
      }
      if (text) return text;
    } catch {}
  }
  return `${fallback} (HTTP ${res.status} ${res.statusText || "Error"})`;
}

  const handleStartReconstruction = async (url: string) => {
    setIsGenerating(true);
    setProgress(5);
    setCurrentStep("Validating URL security and initiating project...");
    setCurrentState("INITIALIZED");
    setLogs(["[INFO] Project initialization request received for: " + url]);
    setErrorMessage(null);

    try {
      // Step 1: Create Project record
      const createRes = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!createRes.ok) {
        const errorDetail = await getErrorMessage(createRes, "Failed to create project");
        throw new Error(errorDetail);
      }

      const newProj = await createRes.json();
      const projId = newProj.id;
      setSelectedProjectId(projId);

      // Step 2: Connect SSE for real-time streaming telemetry
      let pipelineCompleted = false;
      const eventSource = new EventSource(`/api/projects/${projId}/events`);
      eventSource.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.progress !== undefined) setProgress(data.progress);
          if (data.step) {
            setCurrentStep(data.step);
            setLogs((prev) => [...prev, `[INFO] ${data.step}`]);
          }
          if (data.state) {
            setCurrentState(data.state);
            if (data.state === "READY") {
              pipelineCompleted = true;
              eventSource.close();
              fetch(`/api/projects/${projId}`)
                .then((res) => (res.ok ? res.json() : null))
                .then((completed) => {
                  if (completed) {
                    setActiveProject(completed);
                    setProgress(100);
                    setCurrentStep("Reconstruction complete. Local preview is active.");
                    loadProjects();
                  }
                })
                .catch(() => {});
            } else if (data.state === "FAILED") {
              pipelineCompleted = true;
              eventSource.close();
              const failMsg = data.step || "Reconstruction pipeline execution error.";
              setErrorMessage(failMsg);
            }
          }
        } catch (e) {}
      };

      eventSource.onerror = () => {
        // SSE error or closure; polling fallback below guarantees project resolution
      };

      // Step 3: Trigger Generation Pipeline (dispatched asynchronously on backend)
      try {
        const genRes = await fetch(`/api/projects/${projId}/generate`, {
          method: "POST",
        });

        if (genRes.ok) {
          const resProj = await genRes.json();
          if (resProj.status === "READY") {
            pipelineCompleted = true;
            eventSource.close();
            setActiveProject(resProj);
            setProgress(100);
            setCurrentState("READY");
            setCurrentStep("Reconstruction complete. Local preview is active.");
            loadProjects();
          }
        }
      } catch (err) {
        // Network drop during trigger; backend continues execution and SSE / polling handles telemetry
      }

      // Step 4: Active telemetry watchdog / polling fallback (up to 10 minutes for heavy sites)
      if (!pipelineCompleted) {
        for (let i = 0; i < 240; i++) {
          if (pipelineCompleted) break;
          await new Promise((r) => setTimeout(r, 2500));
          if (pipelineCompleted) break;

          try {
            const checkRes = await fetch(`/api/projects/${projId}`);
            if (checkRes.ok) {
              const proj = await checkRes.json();
              if (proj.status === "READY") {
                pipelineCompleted = true;
                eventSource.close();
                setActiveProject(proj);
                setProgress(100);
                setCurrentState("READY");
                setCurrentStep("Reconstruction complete. Local preview is active.");
                loadProjects();
                break;
              } else if (proj.status === "FAILED") {
                pipelineCompleted = true;
                eventSource.close();
                throw new Error(proj.error_message || "Reconstruction pipeline execution error.");
              }
            }
          } catch (pollErr: any) {
            if (pollErr.message && !pollErr.message.includes("fetch")) {
              throw pollErr;
            }
          }
        }
      }

      eventSource.close();

      if (!pipelineCompleted) {
        throw new Error("Reconstruction timed out. Please check telemetry logs or reload the project from below.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred during reconstruction.");
      setCurrentState("FAILED");
      setLogs((prev) => [...prev, `[ERROR] ${err.message}`]);
    }
  };

  const handleCloseModal = () => {
    setIsGenerating(false);
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col">
      <DashboardNavbar />

      <main className="flex-grow">
        {/* Main Hero URL Input Bar */}
        <UrlInputHero
          onStartReconstruction={handleStartReconstruction}
          isLoading={isGenerating && currentState !== "READY" && currentState !== "FAILED"}
        />

        {/* Active Project Workspace */}
        {activeProject && (
          <div className="border-b border-slate-800/80 bg-[#090e1a]/40">
            <ProjectDetailView project={activeProject} onRefresh={loadProjects} />
          </div>
        )}

        {/* Recent Projects Catalog */}
        <ProjectList
          projects={projects}
          onSelectProject={(id) => setSelectedProjectId(id)}
          selectedProjectId={selectedProjectId}
        />
      </main>

      {/* Real-time SSE Agent Progress Modal */}
      <AgentProgressModal
        isOpen={isGenerating}
        progress={progress}
        currentStep={currentStep}
        currentState={currentState}
        logs={logs}
        errorMessage={errorMessage}
        onClose={handleCloseModal}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#060a12] py-8 text-center text-xs text-slate-500">
        <p>Replicate.AI — Autonomous Multi-Stage Frontend Reconstruction Platform.</p>
        <p className="mt-1 text-[11px] text-slate-600">Built for high-impact AI Engineering evaluation. 100% independent React code generation.</p>
      </footer>
    </div>
  );
}
