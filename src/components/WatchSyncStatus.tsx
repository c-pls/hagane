import React, { useEffect, useState } from 'react';
import { Language } from '../types/gym';

export type WatchSyncState =
  | { kind: 'pending' }
  | { kind: 'synced'; at: number }
  | { kind: 'error'; message?: string };

interface Props {
  state: WatchSyncState;
  lang: Language;
  onSyncNow: () => void;
}

function timeAgo(at: number, now: number, lang: Language): string {
  const min = Math.floor((now - at) / 60000);
  if (min < 1) return lang === 'vi' ? 'vừa xong' : 'just now';
  if (min < 60) return lang === 'vi' ? `${min} phút trước` : `${min} min ago`;
  const h = Math.floor(min / 60);
  if (h < 24) return lang === 'vi' ? `${h} giờ trước` : `${h} h ago`;
  const d = Math.floor(h / 24);
  return lang === 'vi' ? `${d} ngày trước` : `${d} d ago`;
}

/** One line on the routine list saying whether the watch has the latest routines. */
export const WatchSyncStatus: React.FC<Props> = ({ state, lang, onSyncNow }) => {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 30000);
    return () => clearInterval(id);
  }, []);

  let dot = 'bg-slate-300';
  let text: string;
  if (state.kind === 'synced') {
    dot = 'bg-emerald-500';
    text =
      lang === 'vi'
        ? `Đã đồng bộ với đồng hồ · ${timeAgo(state.at, now, lang)}`
        : `Synced to watch · ${timeAgo(state.at, now, lang)}`;
  } else if (state.kind === 'error') {
    dot = 'bg-red-500';
    text = lang === 'vi' ? 'Chưa đồng bộ được với đồng hồ' : 'Watch sync failed';
  } else {
    dot = 'bg-amber-400 animate-pulse';
    text = lang === 'vi' ? 'Đang đồng bộ với đồng hồ…' : 'Syncing to watch…';
  }

  return (
    <button
      type="button"
      onClick={onSyncNow}
      aria-label={`${text}. ${lang === 'vi' ? 'Chạm để đồng bộ lại' : 'Tap to sync again'}`}
      className="w-full min-h-[48px] flex items-center gap-3 px-4 rounded-2xl bg-white border border-slate-100 shadow-xs text-left cursor-pointer active:scale-[0.99] transition"
    >
      <span aria-hidden="true" className={`w-2.5 h-2.5 rounded-full shrink-0 ${dot}`} />
      <span className="flex-1 text-sm font-semibold text-slate-700 truncate">{text}</span>
      <span aria-hidden="true" className="text-sm font-bold text-blue-600 shrink-0">
        {lang === 'vi' ? 'Đồng bộ' : 'Sync'}
      </span>
    </button>
  );
};
