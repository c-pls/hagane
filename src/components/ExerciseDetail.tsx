import React, { useEffect, useRef, useState } from 'react';
import { Exercise, Language, Routine } from '../types/gym';
import { translateRoutineText, UI_TEXT } from '../i18n/translations';
import { AnatomicalMuscleMap } from './AnatomicalMuscleMap';

interface ExerciseDetailProps {
  exercise: Exercise;
  lang: Language;
  showComment: boolean;
  comment: string;
  onSaveComment: (comment: string) => void;
  routines?: Routine[];
  onAddExerciseToRoutine?: (
    routineId: string,
    exerciseId: string,
    asWarmup?: boolean,
    replacingExIdx?: number | null
  ) => void;
  activeRoutineId?: string;
  asWarmup?: boolean;
  replacingExIdx?: number | null;
}

export const ExerciseDetail: React.FC<ExerciseDetailProps> = ({
  exercise,
  lang,
  showComment,
  comment,
  onSaveComment,
}) => {
  const t = UI_TEXT[lang];
  const [noteText, setNoteText] = useState(comment);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    setNoteText(comment);
  }, [exercise.id, comment]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(() => {});
    }
  }, [exercise.videoUrl]);

  const activeSteps =
    lang === 'vi' && exercise.stepsVi ? exercise.stepsVi : exercise.steps;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
      {/* LEFT / TOP COLUMN: 1. Seamless Loop Video -> 2. Instructions */}
      <div className="space-y-4">
        {/* 1. CONTINUOUS LOOP VIDEO CARD (At the very top, clean & distraction-free) */}
        <div className="bg-white rounded-[24px] p-3 shadow-xs overflow-hidden">
          <div className="rounded-2xl overflow-hidden bg-white relative flex items-center justify-center min-h-[220px]">
            <video
              ref={videoRef}
              src={exercise.videoUrl}
              autoPlay
              loop
              muted
              playsInline
              disablePictureInPicture
              onContextMenu={(e) => e.preventDefault()}
              className="w-full max-h-[300px] object-contain pointer-events-none select-none"
            />
          </div>
        </div>

        {/* 2. STEP-BY-STEP INSTRUCTIONS DIRECTLY BELOW VIDEO */}
        <div className="space-y-2.5">
          <h3 className="text-lg font-bold text-slate-900 px-1">
            {t.instructionsTitle}
          </h3>

          <div className="bg-white rounded-[24px] p-5 shadow-xs space-y-4">
            {/* Step 1: Prepare & Position */}
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600 block mb-1.5">
                {t.step1Prepare}
              </span>
              <ul className="space-y-1.5 pl-4 list-disc text-sm text-slate-700 leading-relaxed">
                {activeSteps.prepare.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>

            {/* Step 2: Execution */}
            <div className="pt-3 border-t border-slate-100">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 block mb-1.5">
                {t.step2Execution}
              </span>
              <ul className="space-y-1.5 pl-4 list-disc text-sm text-slate-700 leading-relaxed">
                {activeSteps.execution.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>

            {/* Step 3: Breathing & Cues */}
            <div className="pt-3 border-t border-slate-100">
              <span className="text-xs font-bold uppercase tracking-wider text-purple-600 block mb-1.5">
                {t.step3Breathing}
              </span>
              <ul className="space-y-1.5 pl-4 list-disc text-sm text-slate-700 leading-relaxed">
                {activeSteps.breathing.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* 3. ROUTINE-SCOPED COMMENT (Only shown when opened from a Routine) */}
        {showComment && (
          <div className="space-y-2.5">
            <div className="flex items-center justify-between px-1">
              <h3 className="text-lg font-bold text-slate-900">
                {t.commentTitle}
              </h3>
              <button
                onClick={() => onSaveComment(noteText)}
                className="px-3.5 py-1 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition cursor-pointer"
              >
                {t.saveNoteBtn}
              </button>
            </div>
            <div className="bg-white rounded-[24px] p-4 shadow-xs">
              <textarea
                rows={3}
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                onBlur={() => onSaveComment(noteText)}
                placeholder={t.commentPlaceholder}
                className="w-full text-sm text-slate-800 bg-transparent focus:outline-none resize-none placeholder:text-slate-400"
              />
            </div>
          </div>
        )}
      </div>

      {/* RIGHT / BOTTOM COLUMN: DYNAMIC STRENGTHLOG MUSCLE MAP & PRIMARY/SECONDARY LIST */}
      <div>
        <AnatomicalMuscleMap exercise={exercise} lang={lang} />
      </div>
    </div>
  );
};
