import React, { useState } from 'react';
import { Exercise, Language, Routine } from '../types/gym';
import { UI_TEXT } from '../i18n/translations';
import {
  exportBackupJSON,
  parseBackupJSON,
  ShakenBackupPayload,
} from '../services/storage';

interface BackupSyncProps {
  routines: Routine[];
  lang: Language;
  comments: Record<string, string>;
  customExercises: Exercise[];
  onRestoreBackup: (payload: ShakenBackupPayload) => void;
  onShowToast: (msg: string) => void;
}

export const BackupSync: React.FC<BackupSyncProps> = ({
  routines,
  lang,
  comments,
  customExercises,
  onRestoreBackup,
  onShowToast,
}) => {
  const t = UI_TEXT[lang];
  const [importText, setImportText] = useState('');
  const exportedJson = exportBackupJSON(routines, comments, customExercises);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(exportedJson);
      onShowToast(t.toastCopiedJson);
    } catch {
      onShowToast('Select the JSON box and copy manually.');
    }
  };

  const handleDownloadFile = () => {
    const blob = new Blob([exportedJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shaken-gym-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    onShowToast(t.toastDownloadedJson);
  };

  const handleImportCode = () => {
    if (!importText.trim()) return;
    try {
      const parsed = parseBackupJSON(importText);
      onRestoreBackup(parsed);
      setImportText('');
      onShowToast(t.toastRestoredBackup);
    } catch (err) {
      onShowToast(
        err instanceof Error ? err.message : 'Invalid JSON backup code.'
      );
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const text = String(reader.result || '');
        const parsed = parseBackupJSON(text);
        onRestoreBackup(parsed);
        onShowToast(t.toastRestoredBackup);
      } catch {
        onShowToast('Failed to parse uploaded .json file.');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
      {/* Export Card */}
      <div className="bg-white rounded-[24px] p-5 shadow-xs space-y-3.5">
        <div>
          <h3 className="font-bold text-base text-slate-900">
            {t.exportTitle}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">{t.exportSubtitle}</p>
        </div>

        <textarea
          readOnly
          rows={8}
          value={exportedJson}
          className="w-full rounded-2xl bg-slate-900 text-emerald-400 font-mono text-xs p-3.5 focus:outline-none"
        />

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleCopy}
            className="flex-1 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs transition cursor-pointer"
          >
            {t.copyTransferBtn}
          </button>
          <button
            onClick={handleDownloadFile}
            className="flex-1 py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs transition cursor-pointer"
          >
            {t.downloadJsonBtn}
          </button>
        </div>
      </div>

      {/* Import Card */}
      <div className="bg-white rounded-[24px] p-5 shadow-xs space-y-3.5">
        <div>
          <h3 className="font-bold text-base text-slate-900">
            {t.importTitle}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">{t.importSubtitle}</p>
        </div>

        <textarea
          rows={6}
          value={importText}
          onChange={(e) => setImportText(e.target.value)}
          placeholder={t.pasteJsonPlaceholder}
          className="w-full rounded-2xl bg-slate-100 text-slate-800 font-mono text-xs p-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleImportCode}
            className="flex-1 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition cursor-pointer"
          >
            {t.restoreFromCodeBtn}
          </button>
          <label className="flex-1 py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs text-center transition cursor-pointer">
            {t.uploadJsonBtn}
            <input
              type="file"
              accept=".json,application/json"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>
    </div>
  );
};
