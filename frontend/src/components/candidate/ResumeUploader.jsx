import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import LoadingScooter from '../common/LoadingScooter';
import axios from 'axios';
import toast from 'react-hot-toast';

export default function ResumeUploader({ selectedRole, jobDescription, onScoreReceived }) {
  const [file, setFile]         = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage]       = useState('');

  const onDrop = useCallback((accepted) => {
    const pdf = accepted[0];
    if (pdf?.type === 'application/pdf') {
      setFile(pdf);
    } else {
      toast.error('Please upload a PDF file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
  });

  const STAGES = [
    { at: 10, msg: 'Extracting text from PDF…' },
    { at: 30, msg: 'Running spaCy NER analysis…' },
    { at: 55, msg: 'Detecting EV skills…' },
    { at: 75, msg: 'Computing TF-IDF similarity…' },
    { at: 90, msg: 'Generating AI insights…' },
    { at: 100, msg: 'Done! ✅' },
  ];

  const handleUpload = async () => {
    if (!file) { toast.error('Please select a resume'); return; }
    if (!selectedRole) { toast.error('Please select a role first'); return; }

    setUploading(true);
    setProgress(0);

    // Animated progress stages
    let p = 0;
    const tick = setInterval(() => {
      p = Math.min(p + 3, 92);
      setProgress(p);
      const s = STAGES.filter(s => s.at <= p).pop();
      if (s) setStage(s.msg);
    }, 200);

    const formData = new FormData();
    formData.append('resumes', file);
    formData.append('job_description', jobDescription);
    formData.append('role', selectedRole.id);

    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      clearInterval(tick);
      setProgress(100);
      setStage('Done! ✅');

      if (res.data.success && res.data.ranked_candidates?.length > 0) {
        const candidate = res.data.ranked_candidates[0];
        setTimeout(() => {
          onScoreReceived({
            score:     candidate.match_score,
            tfidf:     candidate.tfidf_score,
            skillPct:  candidate.skill_score,
            expPct:    candidate.exp_score,
            skills:    candidate.skills,
            skillMatch: candidate.skill_match,
            summary:   candidate.summary,
            evInsights: candidate.ev_insights,
            name:      candidate.name,
            jobSkills: res.data.job_skills || [],
          });
          setUploading(false);
        }, 600);
      } else {
        toast.error('Could not parse resume. Ensure the PDF has readable text.');
        setUploading(false);
      }
    } catch (err) {
      clearInterval(tick);
      console.error(err);
      toast.error('Upload failed. Is the backend running?');
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Dropzone */}
      {!uploading && (
        <>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-14 text-center cursor-pointer transition-all duration-300 ${
              isDragActive
                ? 'border-ev-primary bg-green-50 scale-[1.02]'
                : 'border-gray-300 hover:border-ev-primary bg-gray-50 hover:bg-green-50/30'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-6xl mb-4">📄</div>
            {isDragActive ? (
              <p className="text-ev-primary font-semibold text-lg">Drop your resume here…</p>
            ) : (
              <>
                <p className="text-gray-600 text-lg font-medium">Drag & drop your resume (PDF)</p>
                <p className="text-sm text-gray-400 mt-2">or click to browse files</p>
              </>
            )}
            <p className="text-xs text-gray-400 mt-3">Supports text-based and scanned PDFs</p>
          </div>

          <AnimatePresence>
            {file && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="mt-4 p-3 bg-green-50 border border-green-200 rounded-xl flex justify-between items-center"
              >
                <span className="text-green-700 font-medium text-sm">✅ {file.name}</span>
                <button onClick={() => setFile(null)} className="text-red-400 hover:text-red-600 text-sm">
                  Remove
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {file && (
            <motion.button
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={handleUpload}
              className="btn-primary w-full mt-5 text-base py-3"
            >
              🚀 Analyze My Resume
            </motion.button>
          )}
        </>
      )}

      {/* Loading */}
      <AnimatePresence>
        {uploading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="mt-4"
          >
            <LoadingScooter progress={progress} label={stage} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
