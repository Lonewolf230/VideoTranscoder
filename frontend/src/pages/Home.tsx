import axios from "axios";
import React, { useRef, useState } from "react";

const base_url = "http://localhost:8000";

type Part = {
  PartNumber: number;
  ETag: string;
};

type Status = "idle" | "uploading" | "done" | "error";

// Progress breakdown:
// 0–10%  → generating multipart upload
// 10–90% → uploading chunks
// 90–100% → completing multipart upload

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

  const formatSize = (bytes: number) => {
    if (bytes >= 1e9) return (bytes / 1e9).toFixed(2) + " GB";
    if (bytes >= 1e6) return (bytes / 1e6).toFixed(1) + " MB";
    return (bytes / 1e3).toFixed(0) + " KB";
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
      console.log("[FILE SELECTED]", file.name, formatSize(file.size));
    }
  };

  const handleUpload = async () => {
    if (!vidfile.current) {
      console.warn("[UPLOAD] No file selected");
      return;
    }

    const file = vidfile.current;
    const chunkSize = 10 * 1024 * 1024; // 10MB
    const totalParts = Math.ceil(file.size / chunkSize);
    parts.current = [];

    setStatus("uploading");

    try {
      setPhaseLabel("Initialising upload…");
      setProgress(0);

      const initRes = await axios.post(base_url + "/create-multipart-upload");
      console.log("[PHASE 1] Multipart upload created. Response:", initRes.data);
      upload_id.current = initRes.data.upload_id;
      fileKey.current = initRes.data.file_key;

      console.log("[PHASE 1] Done. upload_id:", upload_id.current, "file_key:", fileKey.current);
      setProgress(10);

      // ── Phase 2: Get presigned URLs ─────────────────────────────────────
      setPhaseLabel("Preparing chunk URLs…");
      console.log("[PHASE 2] Requesting presigned URLs for", totalParts, "parts...");

      const presignedUrlsRes = await axios.post(base_url + "/part-url", null, {
        params: {
          upload_id: upload_id.current,
          total_parts: totalParts,
          file_key: fileKey.current,
        },
      });

      const presignedUrls: { part_number: number; url: string }[] = presignedUrlsRes.data;
      console.log("[PHASE 2] Presigned URLs received:", presignedUrls.length, "URLs");

      // ── Phase 3: Upload chunks (10% → 90%) ─────────────────────────────
      setPhaseLabel(`Uploading chunks… (0 / ${totalParts})`);
      console.log("[PHASE 3] Starting chunk uploads...");

      let completedParts = 0;

      await Promise.all(
        presignedUrls.map(async ({ part_number: partNumber, url }) => {
          const start = (partNumber - 1) * chunkSize;
          const end = Math.min(start + chunkSize, file.size);
          const chunk = file.slice(start, end);

          console.log(`[CHUNK] Uploading part ${partNumber}/${totalParts} (${formatSize(chunk.size)})...`);

          const res = await axios.put(url, chunk, {
            headers: { "Content-Type": "application/octet-stream" },
          });

          const etag = res.headers.etag;
          parts.current[partNumber - 1] = { PartNumber: partNumber, ETag: etag };
          completedParts += 1;

          const chunkProgress = 10 + Math.round((completedParts / totalParts) * 80);
          setProgress(chunkProgress);
          setPhaseLabel(`Uploading chunks… (${completedParts} / ${totalParts})`);

          console.log(`[CHUNK] Part ${partNumber} done. ETag: ${etag} | Progress: ${chunkProgress}%`);
        })
      );

      console.log("[PHASE 3] All chunks uploaded. Parts:", parts.current);

      // ── Phase 4: Complete multipart upload (90% → 100%) ────────────────
      setPhaseLabel("Completing upload…");
      setProgress(90);
      console.log("[PHASE 4] Completing multipart upload...");

      await axios.post(base_url + "/complete-multipart-upload", {
        upload_id: upload_id.current,
        parts: parts.current,
        file_key: fileKey.current,
      });

      console.log("[PHASE 4] Upload complete!");
      setProgress(100);
      setPhaseLabel("Upload complete!");
      setStatus("done");
    } catch (err) {
      console.error("[ERROR]", err);
      setStatus("error");
      setPhaseLabel("Something went wrong.");
    }
  };

  const totalParts = fileSize ? Math.ceil(fileSize / (10 * 1024 * 1024)) : 0;

  const progressColor =
    status === "done"
      ? "from-green-400 to-emerald-500"
      : status === "error"
      ? "from-red-500 to-red-400"
      : "from-cyan-500";

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6">
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
          <div className={`w-full py-5 px-4 rounded-xl border-2 border-dashed transition-all duration-150 text-center
            ${fileName
              ? "border-violet-600 bg-violet-950/30"
              : "border-zinc-700 hover:border-cyan-600 hover:bg-zinc-800/50"
            }`}>
            {fileName ? (
              <div>
                <p className="text-white font-semibold text-sm truncate">{fileName}</p>
                <p className="text-zinc-400 text-xs mt-1">
                  {fileSize && formatSize(fileSize)} · {totalParts} chunk{totalParts !== 1 ? "s" : ""}
                </p>
              </div>
            ) : (
              <div>
                <p className="text-zinc-400 text-sm">Click to choose a <span className="text-white font-medium">.mp4</span> file</p>
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
          disabled={!fileName || status === "uploading" || status === "done"}
          className="w-full py-3 px-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-150 text-zinc-950 text-sm font-bold tracking-wide"
        >
          {status === "uploading" ? "Uploading…" : status === "done" ? "Uploaded ✓" : "Upload File"}
        </button>

        {/* Progress section */}
        {status !== "idle" && (
          <div className="mt-6 pt-5 border-t border-zinc-800">

            {/* Phase label + percentage */}
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-zinc-400">{phaseLabel}</span>
              <span className="text-xs font-bold text-white tabular-nums">{progress}%</span>
            </div>

            {/* Progress bar */}
            <div className="w-full h-2.5 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${progressColor} transition-all duration-500`}
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Phase markers */}
            <div className="mt-3 flex justify-between text-zinc-600 text-xs">
              <span className={progress >= 10 ? "text-cyan-500" : ""}>Init</span>
              <span className={progress >= 50 ? "text-violet-400" : ""}>Chunks</span>
              <span className={progress === 100 ? "text-green-400" : ""}>Done</span>
            </div>
          </div>
        )}

        {/* Error message */}
        {status === "error" && (
          <p className="mt-4 text-xs text-red-400 text-center">
            Upload failed — check the console for details.
          </p>
        )}

      </div>
    </div>
  );
}