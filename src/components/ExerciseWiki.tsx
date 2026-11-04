import React, { useMemo, useState } from 'react';
import { Exercise, Language } from '../types/gym';
import {
  translateEquipment,
  translateMuscle,
  UI_TEXT,
} from '../i18n/translations';

interface ExerciseWikiProps {
  exercises: Exercise[];
  lang: Language;
  onSelectExercise: (exerciseId: string) => void;
  onAddCustomExercise: (newExercise: Exercise) => void;
}

const MUSCLE_CATEGORIES = [
  'All',
  'Quads',
  'Glutes',
  'Hamstrings',
  'Chest',
  'Back',
  'Shoulders',
  'Biceps',
  'Triceps',
  'Forearms',
  'Core',
  'Calves',
];

const EQUIPMENT_CATEGORIES = [
  'All',
  'Barbell',
  'Dumbbell',
  'Machine',
  'Cable',
  'EZ-Bar',
  'Kettlebell',
  'Bodyweight',
];

const ANATOMY_CHOICES: { label: string; slug: string }[] = [
  { label: 'Quads', slug: 'quadriceps' },
  { label: 'Glutes', slug: 'gluteal' },
  { label: 'Adductors', slug: 'adductors' },
  { label: 'Hamstrings', slug: 'hamstring' },
  { label: 'Calves', slug: 'calves' },
  { label: 'Chest', slug: 'chest' },
  { label: 'Lats / Upper Back', slug: 'upper-back' },
  { label: 'Lower Back', slug: 'lower-back' },
  { label: 'Traps', slug: 'trapezius' },
  { label: 'Delts / Shoulders', slug: 'deltoids' },
  { label: 'Biceps', slug: 'biceps' },
  { label: 'Triceps', slug: 'triceps' },
  { label: 'Forearms', slug: 'forearm' },
  { label: 'Abs', slug: 'abs' },
  { label: 'Obliques', slug: 'obliques' },
];

export const ExerciseWiki: React.FC<ExerciseWikiProps> = ({
  exercises,
  lang,
  onSelectExercise,
  onAddCustomExercise,
}) => {
  const t = UI_TEXT[lang];
  const [search, setSearch] = useState('');
  const [muscleFilter, setMuscleFilter] = useState('All');
  const [equipmentFilter, setEquipmentFilter] = useState('All');
  const [showAddCustom, setShowAddCustom] = useState(false);

  // Custom Exercise Form State
  const [customName, setCustomName] = useState('');
  const [customEquipment, setCustomEquipment] = useState('Barbell');
  const [customVideoUrl, setCustomVideoUrl] = useState('');
  const [customPrimaryIdx, setCustomPrimaryIdx] = useState(0);
  const [customPrepare, setCustomPrepare] = useState('');
  const [customExecution, setCustomExecution] = useState('');
  const [customBreathing, setCustomBreathing] = useState('');

  const filtered = useMemo(() => {
    const normalize = (s: string) =>
      s.toLowerCase().replace(/[-_/(),.]+/g, ' ').replace(/\s+/g, ' ').trim();
    const tokens = normalize(search).split(' ').filter(Boolean);

    return exercises.filter((ex) => {
      const searchableBlob = normalize(
        [
          ex.name,
          ex.nameVi || '',
          ex.equipment,
          ex.category,
          ...ex.primaryMuscles,
          ...ex.secondaryMuscles,
          ...ex.aliases,
        ].join(' ')
      );
      const matchSearch =
        tokens.length === 0 ||
        tokens.every((tok) => searchableBlob.includes(tok));

      const matchMuscle =
        muscleFilter === 'All' ||
        ex.category === muscleFilter ||
        ex.primaryMuscles.some((m) =>
          m.toLowerCase().includes(muscleFilter.toLowerCase())
        ) ||
        ex.secondaryMuscles.some((m) =>
          m.toLowerCase().includes(muscleFilter.toLowerCase())
        );

      const matchEquipment =
        equipmentFilter === 'All' || ex.equipment === equipmentFilter;

      return matchSearch && matchMuscle && matchEquipment;
    });
  }, [exercises, search, muscleFilter, equipmentFilter]);

  const handleCreateCustom = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customName.trim()) return;
    const chosen = ANATOMY_CHOICES[customPrimaryIdx] || ANATOMY_CHOICES[0];
    const newId = `custom-${Date.now()}`;
    const stepsObj = {
      prepare: customPrepare
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean) || ['Set up in starting position.'],
      execution: customExecution
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean) || ['Execute movement with full range of motion.'],
      breathing: customBreathing
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean) || ['Inhale on eccentric, exhale on concentric.'],
    };
    const newEx: Exercise = {
      id: newId,
      slug: customName.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
      name: customName.trim(),
      nameVi: customName.trim(),
      aliases: [],
      category: chosen.label.split(' ')[0],
      equipment: customEquipment,
      videoUrl: customVideoUrl.trim() || exercises[0]?.videoUrl || '',
      primaryMuscles: [chosen.label],
      secondaryMuscles: [],
      primarySlugs: [chosen.slug],
      secondarySlugs: [],
      shortDescription: 'Custom user exercise',
      steps: stepsObj,
      stepsVi: stepsObj,
    };
    onAddCustomExercise(newEx);
    setCustomName('');
    setCustomVideoUrl('');
    setCustomPrepare('');
    setCustomExecution('');
    setCustomBreathing('');
    setShowAddCustom(false);
    onSelectExercise(newId);
  };

  return (
    <div className="space-y-4">
      {/* Header & Search Card */}
      <div className="bg-white rounded-[24px] p-4 shadow-xs space-y-3">
        <div className="flex items-center justify-between gap-2">
          <div>
            <h2 className="font-bold text-base text-slate-900">
              {t.wikiTitle} ({filtered.length})
            </h2>
            <p className="text-xs text-slate-400">{t.wikiSubtitle}</p>
          </div>
          <button
            onClick={() => setShowAddCustom(!showAddCustom)}
            className="px-3.5 py-1.5 rounded-full bg-slate-900 hover:bg-blue-600 text-white text-xs font-bold transition cursor-pointer shrink-0"
          >
            {t.customExerciseBtn}
          </button>
        </div>

        {/* Search Input */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t.searchExercisePlaceholder}
          className="w-full rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        {/* Muscle Filter Pills */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {MUSCLE_CATEGORIES.map((m) => (
              <button
                key={m}
                onClick={() => setMuscleFilter(m)}
                className={`px-3 py-1 rounded-full text-xs font-semibold shrink-0 transition cursor-pointer ${
                  muscleFilter === m
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {translateMuscle(m, lang)}
              </button>
            ))}
          </div>

          {/* Equipment Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {EQUIPMENT_CATEGORIES.map((eq) => (
              <button
                key={eq}
                onClick={() => setEquipmentFilter(eq)}
                className={`px-2.5 py-0.5 rounded-full text-xs font-medium shrink-0 transition cursor-pointer ${
                  equipmentFilter === eq
                    ? 'bg-slate-800 text-white'
                    : 'bg-slate-50 text-slate-500 hover:bg-slate-200 border border-slate-200/70'
                }`}
              >
                {translateEquipment(eq, lang)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Add Custom Exercise Drawer */}
      {showAddCustom && (
        <form
          onSubmit={handleCreateCustom}
          className="bg-white rounded-[24px] p-5 shadow-xs space-y-3 border border-blue-100"
        >
          <h3 className="font-bold text-sm text-slate-900">
            {t.addCustomExerciseTitle}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input
              type="text"
              required
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder={t.customNamePlaceholder}
              className="rounded-xl bg-slate-100 px-3 py-2 text-xs text-slate-900 focus:outline-none"
            />
            <select
              value={customEquipment}
              onChange={(e) => setCustomEquipment(e.target.value)}
              className="rounded-xl bg-slate-100 px-3 py-2 text-xs text-slate-900 focus:outline-none"
            >
              {EQUIPMENT_CATEGORIES.filter((e) => e !== 'All').map((eq) => (
                <option key={eq} value={eq}>
                  {translateEquipment(eq, lang)}
                </option>
              ))}
            </select>
            <select
              value={customPrimaryIdx}
              onChange={(e) => setCustomPrimaryIdx(Number(e.target.value))}
              className="rounded-xl bg-slate-100 px-3 py-2 text-xs text-slate-900 focus:outline-none"
            >
              {ANATOMY_CHOICES.map((ch, idx) => (
                <option key={ch.slug} value={idx}>
                  {t.primaryLabel}: {translateMuscle(ch.label, lang)}
                </option>
              ))}
            </select>
          </div>
          <input
            type="text"
            value={customVideoUrl}
            onChange={(e) => setCustomVideoUrl(e.target.value)}
            placeholder={t.customVideoPlaceholder}
            className="w-full rounded-xl bg-slate-100 px-3 py-2 text-xs text-slate-900 focus:outline-none"
          />
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <textarea
              rows={2}
              value={customPrepare}
              onChange={(e) => setCustomPrepare(e.target.value)}
              placeholder={t.customPrepPlaceholder}
              className="rounded-xl bg-slate-100 p-2.5 text-xs text-slate-900 focus:outline-none"
            />
            <textarea
              rows={2}
              value={customExecution}
              onChange={(e) => setCustomExecution(e.target.value)}
              placeholder={t.customExecPlaceholder}
              className="rounded-xl bg-slate-100 p-2.5 text-xs text-slate-900 focus:outline-none"
            />
            <textarea
              rows={2}
              value={customBreathing}
              onChange={(e) => setCustomBreathing(e.target.value)}
              placeholder={t.customBreathPlaceholder}
              className="rounded-xl bg-slate-100 p-2.5 text-xs text-slate-900 focus:outline-none"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddCustom(false)}
              className="px-4 py-1.5 rounded-xl bg-slate-100 text-slate-600 text-xs font-bold cursor-pointer"
            >
              {t.cancel}
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-xl bg-blue-600 text-white text-xs font-bold cursor-pointer"
            >
              {t.saveExerciseBtn}
            </button>
          </div>
        </form>
      )}

      {/* Exercise Cards Grid (Clean Wiki — no routine comment pins) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filtered.map((ex) => {
          const displayName =
            lang === 'vi' && ex.nameVi ? ex.nameVi : ex.name;
          return (
            <div
              key={ex.id}
              onClick={() => onSelectExercise(ex.id)}
              className="bg-white rounded-[22px] p-4 shadow-xs hover:shadow-md cursor-pointer transition flex items-center justify-between gap-3"
            >
              <div className="min-w-0 space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm text-slate-900 truncate">
                    {displayName}
                  </h3>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-xs font-medium shrink-0">
                    {translateEquipment(ex.equipment, lang)}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  {t.primaryLabel}:{' '}
                  <span className="text-slate-700 font-semibold">
                    {ex.primaryMuscles
                      .map((m) => translateMuscle(m, lang))
                      .join(', ')}
                  </span>
                </p>
              </div>

              <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-700 font-serif italic font-bold text-sm flex items-center justify-center shrink-0">
                i
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
