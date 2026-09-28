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
          setSelectedProjectId(data[0].id);
          setActiveProject(data[0]);
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
        const errData = await createRes.json();
        throw new Error(errData.detail || "Failed to create project.");
      }

      const newProj = await createRes.json();
      const projId = newProj.id;
      setSelectedProjectId(projId);

      // Step 2: Connect SSE for real-time streaming telemetry
      const eventSource = new EventSource(`/api/projects/${projId}/events`);
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.progress !== undefined) setProgress(data.progress);
          if (data.step) {
            setCurrentStep(data.step);
            setLogs((prev) => [...prev, `[INFO] ${data.step}`]);
          }
          if (data.state) setCurrentState(data.state);
        } catch (e) {}
      };

      eventSource.onerror = () => {
        eventSource.close();
      };

      // Step 3: Trigger Generation Pipeline
      const genRes = await fetch(`/api/projects/${projId}/generate`, {
        method: "POST",
      });

      eventSource.close();

      if (!genRes.ok) {
        const err = await genRes.json();
        throw new Error(err.detail || "Reconstruction pipeline execution error.");
      }

      const completedProj = await genRes.json();
      setActiveProject(completedProj);
      setProgress(100);
      setCurrentState("READY");
      setCurrentStep("Reconstruction complete. Local preview is active.");
      loadProjects();
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
