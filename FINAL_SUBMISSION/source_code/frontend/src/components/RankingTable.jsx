export default function RankingTable({ rankings, onSelect, selectedId }) {
  if (!rankings || !rankings.length) {
    return <p className="mt-5 text-sm text-slate-500">No ranked candidates available yet.</p>;
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-slate-600">
          <tr>
            <th className="px-4 py-4 text-left font-semibold">Candidate</th>
            <th className="px-4 py-4 text-left font-semibold">Skill match</th>
            <th className="px-4 py-4 text-left font-semibold">Final score</th>
            <th className="px-4 py-4 text-left font-semibold">Strengths</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {rankings.map((row) => (
            <tr
              key={row.candidate?.id || row.candidate_id}
              onClick={() => onSelect(row)}
              className={`cursor-pointer transition hover:bg-slate-50 ${((row.candidate?.id || row.candidate_id) === selectedId) ? 'bg-sky-50' : ''}`}
            >
              <td className="px-4 py-4 font-medium text-slate-900">{row.candidate?.full_name || 'Unknown candidate'}</td>
              <td className="px-4 py-4 text-slate-600">{Math.round(row.skill_score || 0)}%</td>
              <td className="px-4 py-4 text-slate-900">{Math.round(row.final_score || 0)}%</td>
              <td className="px-4 py-4 text-slate-500">{(row.strengths || []).slice(0, 2).join(', ') || 'No summary'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
