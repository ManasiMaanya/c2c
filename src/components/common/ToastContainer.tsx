import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react';
import { useDemo, ToastMessage } from '../../context/DemoContext';

export const ToastContainer: React.FC = () => {
  const { toasts, dismissToast } = useDemo();

  if (!toasts || toasts.length === 0) return null;

  const icons = {
    info: <Info className="w-4 h-4 text-cyan-400 shrink-0" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />,
    error: <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />,
    success: <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
  };

  const borders = {
    info: 'border-cyan-500/40 bg-slate-900/95 shadow-glow-cyan',
    warning: 'border-amber-500/40 bg-amber-950/90 shadow-[0_0_20px_rgba(245,158,11,0.2)]',
    error: 'border-red-500/50 bg-red-950/90 shadow-glow-red',
    success: 'border-emerald-500/40 bg-emerald-950/90 shadow-glow-green'
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none">
      {toasts.map((toast: ToastMessage) => (
        <div
          key={toast.id}
          className={`pointer-events-auto p-3.5 rounded-xl border backdrop-blur-md flex items-start gap-3 transition-all duration-300 transform translate-y-0 animate-in slide-in-from-bottom-5 ${borders[toast.type]}`}
        >
          {icons[toast.type]}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-100 font-mono tracking-tight">{toast.title}</h4>
              <span className="text-[9px] font-mono text-slate-400">{toast.timestamp}</span>
            </div>
            <p className="text-[11px] text-slate-300 mt-0.5 leading-snug">{toast.description}</p>
          </div>
          <button
            onClick={() => dismissToast(toast.id)}
            className="text-slate-500 hover:text-slate-300 p-0.5 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};
