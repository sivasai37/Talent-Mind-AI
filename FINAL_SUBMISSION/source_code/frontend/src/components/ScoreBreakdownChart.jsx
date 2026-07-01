export default function ScoreBreakdownChart({ data }) {
  return (
    <div className="mt-6 space-y-4">
      {data.map((entry) => (
        <div key={entry.name} className="space-y-2">
          <div className="flex items-center justify-between text-sm text-slate-700">
            <span>{entry.name}</span>
            <span className="font-semibold">{Math.round(entry.score)}%</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-sky-600 transition-all duration-300"
              style={{ width: `${Math.min(Math.max(entry.score, 0), 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
