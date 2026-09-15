import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, Video, UploadCloud, X, Check, Loader2, AlertCircle } from "lucide-react";

export default function TelemetryModal({ task, onClose, onSubmitSuccess }) {
  const [mediaPreview, setMediaPreview] = useState(null);
  const [userNotes, setUserNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const isVideo = task.input_type === "video";

  const handleFileCapture = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check size limit: 25MB
    if (file.size > 25 * 1024 * 1024) {
      setError("File exceeds maximum size of 25MB.");
      return;
    }

    setError("");
    const reader = new FileReader();
    reader.onload = () => {
      setMediaPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!mediaPreview) {
      setError("Please capture or select an image/video to proceed.");
      return;
    }

    setSubmitting(true);
    try {
      await onSubmitSuccess(task.task_id, {
        inputGiven: mediaPreview,
        userNotes: userNotes.trim() || "No symptoms reported by patient.",
      });
      onClose();
    } catch (err) {
      console.error(err);
      setError("Failed to process telemetry submission. Try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-lg bg-white rounded-3xl shadow-xl overflow-hidden flex flex-col"
      >
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              {isVideo ? <Video className="w-5 h-5" /> : <Camera className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="font-bold text-slate-800 text-sm">{task.instructions}</h3>
              <p className="text-[11px] text-slate-400 capitalize">{task.input_type} Evaluation Check</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-100 text-xs">
            <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px] block mb-0.5">
              Protocol Evaluation Parameter
            </span>
            <p className="text-slate-700">{task.things_to_evaluate}</p>
          </div>

          <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-200 hover:border-indigo-400 rounded-2xl p-4 bg-slate-50/50 transition-colors">
            <input
              type="file"
              ref={fileInputRef}
              accept={isVideo ? "video/*" : "image/*"}
              capture="environment"
              onChange={handleFileCapture}
              className="hidden"
            />

            {mediaPreview ? (
              <div className="w-full flex flex-col items-center gap-2">
                {isVideo ? (
                  <video src={mediaPreview} controls className="max-h-52 w-auto rounded-xl border border-slate-200" />
                ) : (
                  <img src={mediaPreview} alt="Preview" className="max-h-52 w-auto rounded-xl object-contain border border-slate-200" />
                )}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
                >
                  Retake / Select Different File
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center gap-2 py-6 text-slate-500 hover:text-indigo-600 transition-colors"
              >
                <div className="p-3 bg-white rounded-full shadow-xs border border-slate-200">
                  <UploadCloud className="w-6 h-6 text-indigo-600" />
                </div>
                <span className="text-xs font-semibold">
                  Tap to record or select {isVideo ? "video" : "photograph"}
                </span>
                <span className="text-[11px] text-slate-400">Clear lighting is recommended</span>
              </button>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Patient Remarks / Symptoms (Optional)
            </label>
            <textarea
              rows={2}
              value={userNotes}
              onChange={(e) => setUserNotes(e.target.value)}
              placeholder="e.g. Incision feels slightly itchy, no drainage seen..."
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
            />
          </div>

          {error && (
            <div className="flex items-center gap-1.5 text-xs text-red-600 bg-red-50 p-2.5 rounded-xl">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !mediaPreview}
              className="flex items-center gap-1.5 px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 rounded-xl shadow-xs transition-colors"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing Telemetry...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  Submit Check-in
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}