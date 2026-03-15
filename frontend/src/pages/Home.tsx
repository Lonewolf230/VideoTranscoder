// import axios from "axios";
// import React, { useRef, useState } from "react";
// const base_url = "http://localhost:8000";

// type Part = {
//   PartNumber: number;
//   ETag: string;
// };

// type Status = "idle" | "uploading" | "done" | "error";

// // Progress breakdown:
// // 0–10%  → generating multipart upload
// // 10–90% → uploading chunks
// // 90–100% → completing multipart upload

// export default function Home() {
//   const upload_id = useRef<string | null>(null);
//   const parts = useRef<Part[]>([]);
//   const vidfile = useRef<File | null>(null);
//   const fileKey = useRef<string>("");

//   const [fileName, setFileName] = useState<string | null>(null);
//   const [fileSize, setFileSize] = useState<number | null>(null);
//   const [status, setStatus] = useState<Status>("idle");
//   const [progress, setProgress] = useState(0);
//   const [phaseLabel, setPhaseLabel] = useState("");

//   const formatSize = (bytes: number) => {
//     if (bytes >= 1e9) return (bytes / 1e9).toFixed(2) + " GB";
//     if (bytes >= 1e6) return (bytes / 1e6).toFixed(1) + " MB";
//     return (bytes / 1e3).toFixed(0) + " KB";
//   };

//   const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
//     const file = e.target.files?.[0] ?? null;
//     if (file) {
//       vidfile.current = file;
//       setFileName(file.name);
//       setFileSize(file.size);
//       setProgress(0);
//       setStatus("idle");
//       setPhaseLabel("");
//       console.log("[FILE SELECTED]", file.name, formatSize(file.size));
//     }
//   };

//   const handleUpload = async () => {
//     if (!vidfile.current) {
//       console.warn("[UPLOAD] No file selected");
//       return;
//     }

//     const file = vidfile.current;
//     const chunkSize = 10 * 1024 * 1024; // 10MB
//     const totalParts = Math.ceil(file.size / chunkSize);
//     parts.current = [];

//     setStatus("uploading");

//     try {
//       setPhaseLabel("Initialising upload…");
//       setProgress(0);

//       const initRes = await axios.post(base_url + "/create-multipart-upload");
//       console.log("[PHASE 1] Multipart upload created. Response:", initRes.data);
//       upload_id.current = initRes.data.upload_id;
//       fileKey.current = initRes.data.file_key;

//       console.log("[PHASE 1] Done. upload_id:", upload_id.current, "file_key:", fileKey.current);
//       setProgress(10);

//       // ── Phase 2: Get presigned URLs ─────────────────────────────────────
//       setPhaseLabel("Preparing chunk URLs…");
//       console.log("[PHASE 2] Requesting presigned URLs for", totalParts, "parts...");

//       const presignedUrlsRes = await axios.post(base_url + "/part-url", null, {
//         params: {
//           upload_id: upload_id.current,
//           total_parts: totalParts,
//           file_key: fileKey.current,
//         },
//       });

//       const presignedUrls: { part_number: number; url: string }[] = presignedUrlsRes.data;
//       console.log("[PHASE 2] Presigned URLs received:", presignedUrls.length, "URLs");

//       // ── Phase 3: Upload chunks (10% → 90%) ─────────────────────────────
//       setPhaseLabel(`Uploading chunks… (0 / ${totalParts})`);
//       console.log("[PHASE 3] Starting chunk uploads...");

//       let completedParts = 0;

//       await Promise.all(
//         presignedUrls.map(async ({ part_number: partNumber, url }) => {
//           const start = (partNumber - 1) * chunkSize;
//           const end = Math.min(start + chunkSize, file.size);
//           const chunk = file.slice(start, end);

//           console.log(`[CHUNK] Uploading part ${partNumber}/${totalParts} (${formatSize(chunk.size)})...`);

//           const res = await axios.put(url, chunk, {
//             headers: { "Content-Type": "application/octet-stream" },
//           });

//           const etag = res.headers.etag;
//           parts.current[partNumber - 1] = { PartNumber: partNumber, ETag: etag };
//           completedParts += 1;

//           const chunkProgress = 10 + Math.round((completedParts / totalParts) * 80);
//           setProgress(chunkProgress);
//           setPhaseLabel(`Uploading chunks… (${completedParts} / ${totalParts})`);

//           console.log(`[CHUNK] Part ${partNumber} done. ETag: ${etag} | Progress: ${chunkProgress}%`);
//         })
//       );

//       console.log("[PHASE 3] All chunks uploaded. Parts:", parts.current);

//       // ── Phase 4: Complete multipart upload (90% → 100%) ────────────────
//       setPhaseLabel("Completing upload…");
//       setProgress(90);
//       console.log("[PHASE 4] Completing multipart upload...");

//       await axios.post(base_url + "/complete-multipart-upload", {
//         upload_id: upload_id.current,
//         parts: parts.current,
//         file_key: fileKey.current,
//       });

//       console.log("[PHASE 4] Upload complete!");
//       setProgress(100);
//       setPhaseLabel("Upload complete!");
//       setStatus("done");
//     } catch (err) {
//       console.error("[ERROR]", err);
//       setStatus("error");
//       setPhaseLabel("Something went wrong.");
//     }
//   };

//   const totalParts = fileSize ? Math.ceil(fileSize / (10 * 1024 * 1024)) : 0;

//   const progressColor =
//     status === "done"
//       ? "from-green-400 to-emerald-500"
//       : status === "error"
//         ? "from-red-500 to-red-400"
//         : "from-cyan-500";

//   return (
//     <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6">
//       <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-2xl">

//         {/* Header */}
//         <div className="mb-8">
//           <span className="text-xs font-semibold tracking-widest text-cyan-400 uppercase">
//             S3 Multipart
//           </span>
//           <h1 className="mt-1 text-2xl font-bold text-white tracking-tight">
//             Video Uploader
//           </h1>
//           <p className="mt-1 text-sm text-zinc-500">
//             Select a file and hit upload — we handle the rest
//           </p>
//         </div>

//         {/* File picker */}
//         <label className="block w-full cursor-pointer mb-4">
//           <div className={`w-full py-5 px-4 rounded-xl border-2 border-dashed transition-all duration-150 text-center
//             ${fileName
//               ? "border-violet-600 bg-violet-950/30"
//               : "border-zinc-700 hover:border-cyan-600 hover:bg-zinc-800/50"
//             }`}>
//             {fileName ? (
//               <div>
//                 <p className="text-white font-semibold text-sm truncate">{fileName}</p>
//                 <p className="text-zinc-400 text-xs mt-1">
//                   {fileSize && formatSize(fileSize)} · {totalParts} chunk{totalParts !== 1 ? "s" : ""}
//                 </p>
//               </div>
//             ) : (
//               <div>
//                 <p className="text-zinc-400 text-sm">Click to choose a <span className="text-white font-medium">.mp4</span> file</p>
//                 <p className="text-zinc-600 text-xs mt-1">10 MB chunks</p>
//               </div>
//             )}
//           </div>
//           <input
//             type="file"
//             accept=".mp4"
//             onChange={onFileChange}
//             disabled={status === "uploading"}
//             className="sr-only"
//           />
//         </label>

//         {/* Upload button */}
//         <button
//           onClick={handleUpload}
//           disabled={!fileName || status === "uploading" || status === "done"}
//           className="w-full py-3 px-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-150 text-zinc-950 text-sm font-bold tracking-wide"
//         >
//           {status === "uploading" ? "Uploading…" : status === "done" ? "Uploaded ✓" : "Upload File"}
//         </button>

//         {/* Progress section */}
//         {status !== "idle" && (
//           <div className="mt-6 pt-5 border-t border-zinc-800">

//             {/* Phase label + percentage */}
//             <div className="flex justify-between items-center mb-2">
//               <span className="text-xs text-zinc-400">{phaseLabel}</span>
//               <span className="text-xs font-bold text-white tabular-nums">{progress}%</span>
//             </div>

//             {/* Progress bar */}
//             <div className="w-full h-2.5 bg-zinc-800 rounded-full overflow-hidden">
//               <div
//                 className={`h-full rounded-full bg-gradient-to-r ${progressColor} transition-all duration-500`}
//                 style={{ width: `${progress}%` }}
//               />
//             </div>

//             {/* Phase markers */}
//             <div className="mt-3 flex justify-between text-zinc-600 text-xs">
//               <span className={progress >= 10 ? "text-cyan-500" : ""}>Init</span>
//               <span className={progress >= 50 ? "text-violet-400" : ""}>Chunks</span>
//               <span className={progress === 100 ? "text-green-400" : ""}>Done</span>
//             </div>
//           </div>
//         )}

//         {/* Error message */}
//         {status === "error" && (
//           <p className="mt-4 text-xs text-red-400 text-center">
//             Upload failed — check the console for details.
//           </p>
//         )}

//       </div>      
//     </div>
//   );
// }

import axios from "axios";
import React, { useRef, useState } from "react";

const base_url = "http://localhost:8000";

type Part = {
  PartNumber: number;
  ETag: string;
};

type Status = "idle" | "uploading" | "done" | "error";

type JobStatus =
  | "uploading"
  | "processing"
  | "transcoding"
  | "ready"
  | "failed";

type Job = {
  id: string;
  fileName: string;
  fileSize: number;
  uploadProgress: number;
  status: JobStatus;
  createdAt: Date;
  downloadUrl?: string;
  errorMessage?: string;
};

// ─── Job Card ────────────────────────────────────────────────────────────────

function JobCard({
  job,
  onRetry,
}: {
  job: Job;
  onRetry: (id: string) => void;
}) {
  const formatSize = (bytes: number) => {
    if (bytes >= 1e9) return (bytes / 1e9).toFixed(2) + " GB";
    if (bytes >= 1e6) return (bytes / 1e6).toFixed(1) + " MB";
    return (bytes / 1e3).toFixed(0) + " KB";
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const statusConfig: Record<
    JobStatus,
    { label: string; color: string; dot: string; showBar: boolean }
  > = {
    uploading: {
      label: "Uploading",
      color: "text-cyan-400",
      dot: "bg-cyan-400 animate-pulse",
      showBar: true,
    },
    processing: {
      label: "Processing",
      color: "text-violet-400",
      dot: "bg-violet-400 animate-pulse",
      showBar: false,
    },
    transcoding: {
      label: "Transcoding",
      color: "text-amber-400",
      dot: "bg-amber-400 animate-pulse",
      showBar: false,
    },
    ready: {
      label: "Ready",
      color: "text-emerald-400",
      dot: "bg-emerald-400",
      showBar: false,
    },
    failed: {
      label: "Failed",
      color: "text-red-400",
      dot: "bg-red-400",
      showBar: false,
    },
  };

  const cfg = statusConfig[job.status];

  return (
    <div
      className="group relative rounded-xl border border-zinc-800 bg-zinc-900/80 p-4 transition-all duration-200 hover:border-zinc-700 hover:bg-zinc-900"
      style={{ animation: "slideIn 0.25s ease-out both" }}
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-white truncate leading-tight">
            {job.fileName}
          </p>
          <p className="text-xs text-zinc-500 mt-0.5">
            {formatSize(job.fileSize)} · {formatTime(job.createdAt)}
          </p>
        </div>

        {/* Status badge */}
        <div className="flex items-center gap-1.5 shrink-0">
          <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
          <span className={`text-xs font-semibold ${cfg.color}`}>
            {cfg.label}
          </span>
        </div>
      </div>

      {/* Progress bar (only while uploading) */}
      {cfg.showBar && (
        <div className="mb-3">
          <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all duration-500"
              style={{ width: `${job.uploadProgress}%` }}
            />
          </div>
          <p className="text-xs text-zinc-500 mt-1 tabular-nums">
            {job.uploadProgress}%
          </p>
        </div>
      )}

      {/* Indeterminate shimmer for processing/transcoding */}
      {(job.status === "processing" || job.status === "transcoding") && (
        <div className="mb-3">
          <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full"
              style={{
                background:
                  job.status === "transcoding"
                    ? "linear-gradient(90deg, #f59e0b, #f97316)"
                    : "linear-gradient(90deg, #8b5cf6, #a78bfa)",
                animation: "shimmer 1.6s ease-in-out infinite",
                width: "45%",
              }}
            />
          </div>
        </div>
      )}

      {/* Error message */}
      {job.status === "failed" && job.errorMessage && (
        <p className="text-xs text-red-400/80 mb-2">{job.errorMessage}</p>
      )}

      {/* Action buttons */}
      <div className="flex gap-2 mt-1">
        {job.status === "ready" && job.downloadUrl && (
          <a
            href={job.downloadUrl}
            download
            className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4"
              />
            </svg>
            Download
          </a>
        )}

        {job.status === "failed" && (
          <button
            onClick={() => onRetry(job.id)}
            className="flex items-center gap-1.5 text-xs font-semibold text-red-400 hover:text-red-300 transition-colors"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 4v5h5M20 20v-5h-5M4 9a9 9 0 0114.9-3.4M20 15a9 9 0 01-14.9 3.4"
              />
            </svg>
            Retry
          </button>
        )}

        {job.status === "ready" && (
          <button className="flex items-center gap-1.5 text-xs font-semibold text-zinc-500 hover:text-zinc-300 transition-colors">
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4"
              />
            </svg>
            Re-upload
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Sidebar ─────────────────────────────────────────────────────────────────

function Sidebar({
  jobs,
  onRetry,
  onClear,
}: {
  jobs: Job[];
  onRetry: (id: string) => void;
  onClear: () => void;
}) {
  const counts = {
    uploading: jobs.filter((j) => j.status === "uploading").length,
    active: jobs.filter(
      (j) => j.status === "processing" || j.status === "transcoding"
    ).length,
    ready: jobs.filter((j) => j.status === "ready").length,
    failed: jobs.filter((j) => j.status === "failed").length,
  };

  return (
    <div className="w-80 shrink-0 flex flex-col h-screen bg-zinc-950 border-l border-zinc-800/70">
      {/* Sidebar header */}
      <div className="px-5 py-5 border-b border-zinc-800/70">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold tracking-widest text-zinc-500 uppercase">
              Upload Queue
            </p>
            <h2 className="mt-0.5 text-base font-bold text-white">
              {jobs.length} job{jobs.length !== 1 ? "s" : ""}
            </h2>
          </div>
          {jobs.length > 0 && (
            <button
              onClick={onClear}
              className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors"
            >
              Clear all
            </button>
          )}
        </div>

        {jobs.length > 0 && (
          <div className="flex gap-2 mt-3 flex-wrap">
            {counts.uploading > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-medium">
                {counts.uploading} uploading
              </span>
            )}
            {counts.active > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 text-xs font-medium">
                {counts.active} processing
              </span>
            )}
            {counts.ready > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium">
                {counts.ready} ready
              </span>
            )}
            {counts.failed > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 text-xs font-medium">
                {counts.failed} failed
              </span>
            )}
          </div>
        )}
      </div>

      {/* Job list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full pb-16 text-center">
            <div className="w-12 h-12 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-3">
              <svg
                className="w-5 h-5 text-zinc-700"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <p className="text-sm text-zinc-600">No uploads yet</p>
            <p className="text-xs text-zinc-700 mt-1">
              Jobs appear here as you upload
            </p>
          </div>
        ) : (
          // Most recent first
          [...jobs].reverse().map((job) => (
            <JobCard key={job.id} job={job} onRetry={onRetry} />
          ))
        )}
      </div>
    </div>
  );
}

// ─── Home ─────────────────────────────────────────────────────────────────────

export default function Home() {
  const upload_id = useRef<string | null>(null);
  const parts = useRef<Part[]>([]);
  const vidfile = useRef<File | null>(null);
  const fileKey = useRef<string>("");

  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<number | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [progress, setProgress] = useState(0);
  const [phaseLabel, setPhaseLabel] = useState("");

  const [jobs, setJobs] = useState<Job[]>([]);

  const formatSize = (bytes: number) => {
    if (bytes >= 1e9) return (bytes / 1e9).toFixed(2) + " GB";
    if (bytes >= 1e6) return (bytes / 1e6).toFixed(1) + " MB";
    return (bytes / 1e3).toFixed(0) + " KB";
  };

  // Helper to update a job in state
  const updateJob = (id: string, patch: Partial<Job>) => {
    setJobs((prev) =>
      prev.map((j) => (j.id === id ? { ...j, ...patch } : j))
    );
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    if (file) {
      vidfile.current = file;
      setFileName(file.name);
      setFileSize(file.size);
      setProgress(0);
      setStatus("idle");
      setPhaseLabel("");
    }
  };

  const handleUpload = async () => {
    if (!vidfile.current) return;

    const file = vidfile.current;
    const chunkSize = 10 * 1024 * 1024;
    const totalParts = Math.ceil(file.size / chunkSize);
    parts.current = [];

    // Create a job immediately
    const jobId = crypto.randomUUID();
    const newJob: Job = {
      id: jobId,
      fileName: file.name,
      fileSize: file.size,
      uploadProgress: 0,
      status: "uploading",
      createdAt: new Date(),
    };
    setJobs((prev) => [...prev, newJob]);

    setStatus("uploading");

    try {
      setPhaseLabel("Initialising upload…");
      setProgress(0);

      const initRes = await axios.post(base_url + "/create-multipart-upload");
      upload_id.current = initRes.data.upload_id;
      fileKey.current = initRes.data.file_key;
      setProgress(10);
      updateJob(jobId, { uploadProgress: 10 });

      setPhaseLabel("Preparing chunk URLs…");
      const presignedUrlsRes = await axios.post(base_url + "/part-url", null, {
        params: {
          upload_id: upload_id.current,
          total_parts: totalParts,
          file_key: fileKey.current,
        },
      });

      const presignedUrls: { part_number: number; url: string }[] =
        presignedUrlsRes.data;

      setPhaseLabel(`Uploading chunks… (0 / ${totalParts})`);
      let completedParts = 0;

      await Promise.all(
        presignedUrls.map(async ({ part_number: partNumber, url }) => {
          const start = (partNumber - 1) * chunkSize;
          const end = Math.min(start + chunkSize, file.size);
          const chunk = file.slice(start, end);

          const res = await axios.put(url, chunk, {
            headers: { "Content-Type": "application/octet-stream" },
          });

          const etag = res.headers.etag;
          parts.current[partNumber - 1] = { PartNumber: partNumber, ETag: etag };
          completedParts += 1;

          const chunkProgress = 10 + Math.round((completedParts / totalParts) * 80);
          setProgress(chunkProgress);
          setPhaseLabel(
            `Uploading chunks… (${completedParts} / ${totalParts})`
          );
          updateJob(jobId, { uploadProgress: chunkProgress });
        })
      );

      setPhaseLabel("Completing upload…");
      setProgress(90);
      updateJob(jobId, { uploadProgress: 90 });

      const completeRes = await axios.post(
        base_url + "/complete-multipart-upload",
        {
          upload_id: upload_id.current,
          parts: parts.current,
          file_key: fileKey.current,
        }
      );

      setProgress(100);
      setPhaseLabel("Upload complete!");
      setStatus("done");

      // Transition job → processing, then simulate transcoding → ready
      updateJob(jobId, { uploadProgress: 100, status: "processing" });

      // Simulate post-upload pipeline stages
      // In production, replace these timeouts with real polling / websocket updates
      setTimeout(() => updateJob(jobId, { status: "transcoding" }), 2500);
      setTimeout(() => {
        updateJob(jobId, {
          status: "ready",
          downloadUrl: completeRes.data?.download_url ?? "#",
        });
      }, 6000);
    } catch (err) {
      console.error("[ERROR]", err);
      setStatus("error");
      setPhaseLabel("Something went wrong.");
      updateJob(jobId, {
        status: "failed",
        errorMessage: "Upload failed. Check console for details.",
      });
    }
  };

  const handleRetry = (id: string) => {
    // Reset the job and let the user re-select + upload manually.
    // You could auto-trigger a retry here if you persist file refs per job.
    setJobs((prev) => prev.filter((j) => j.id !== id));
    setStatus("idle");
    setProgress(0);
    setPhaseLabel("");
    setFileName(null);
    setFileSize(null);
    vidfile.current = null;
  };

  const handleClearAll = () => {
    setJobs([]);
  };

  const totalParts = fileSize ? Math.ceil(fileSize / (10 * 1024 * 1024)) : 0;

  const progressColor =
    status === "done"
      ? "from-green-400 to-emerald-500"
      : status === "error"
      ? "from-red-500 to-red-400"
      : "from-cyan-500 to-violet-500";

  return (
    <>
      {/* Keyframe animations injected once */}
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes shimmer {
          0%   { transform: translateX(-120%); }
          100% { transform: translateX(280%); }
        }
      `}</style>

      <div className="flex h-screen bg-zinc-950 overflow-hidden">
        {/* ── Main uploader panel ── */}
        <div className="flex-1 flex items-center justify-center p-6 overflow-y-auto">
          <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-2xl">
            {/* Header */}
            <div className="mb-8">
              <span className="text-xs font-semibold tracking-widest text-cyan-400 uppercase">
                S3 Multipart
              </span>
              <h1 className="mt-1 text-2xl font-bold text-white tracking-tight">
                Video Uploader
              </h1>
              <p className="mt-1 text-sm text-zinc-500">
                Select a file and hit upload — we handle the rest
              </p>
            </div>

            {/* File picker */}
            <label className="block w-full cursor-pointer mb-4">
              <div
                className={`w-full py-5 px-4 rounded-xl border-2 border-dashed transition-all duration-150 text-center
                  ${
                    fileName
                      ? "border-violet-600 bg-violet-950/30"
                      : "border-zinc-700 hover:border-cyan-600 hover:bg-zinc-800/50"
                  }`}
              >
                {fileName ? (
                  <div>
                    <p className="text-white font-semibold text-sm truncate">
                      {fileName}
                    </p>
                    <p className="text-zinc-400 text-xs mt-1">
                      {fileSize && formatSize(fileSize)} · {totalParts} chunk
                      {totalParts !== 1 ? "s" : ""}
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-zinc-400 text-sm">
                      Click to choose a{" "}
                      <span className="text-white font-medium">.mp4</span> file
                    </p>
                    <p className="text-zinc-600 text-xs mt-1">10 MB chunks</p>
                  </div>
                )}
              </div>
              <input
                type="file"
                accept=".mp4"
                onChange={onFileChange}
                disabled={status === "uploading"}
                className="sr-only"
              />
            </label>

            {/* Upload button */}
            <button
              onClick={handleUpload}
              disabled={
                !fileName || status === "uploading" || status === "done"
              }
              className="w-full py-3 px-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-150 text-zinc-950 text-sm font-bold tracking-wide"
            >
              {status === "uploading"
                ? "Uploading…"
                : status === "done"
                ? "Uploaded ✓"
                : "Upload File"}
            </button>

            {/* Progress section */}
            {status !== "idle" && (
              <div className="mt-6 pt-5 border-t border-zinc-800">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-zinc-400">{phaseLabel}</span>
                  <span className="text-xs font-bold text-white tabular-nums">
                    {progress}%
                  </span>
                </div>

                <div className="w-full h-2.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${progressColor} transition-all duration-500`}
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <div className="mt-3 flex justify-between text-zinc-600 text-xs">
                  <span className={progress >= 10 ? "text-cyan-500" : ""}>
                    Init
                  </span>
                  <span className={progress >= 50 ? "text-violet-400" : ""}>
                    Chunks
                  </span>
                  <span className={progress === 100 ? "text-green-400" : ""}>
                    Done
                  </span>
                </div>
              </div>
            )}

            {status === "error" && (
              <p className="mt-4 text-xs text-red-400 text-center">
                Upload failed — check the console for details.
              </p>
            )}
          </div>
        </div>

        <Sidebar jobs={jobs} onRetry={handleRetry} onClear={handleClearAll} />
      </div>
    </>
  );
}