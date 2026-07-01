import ScoreBreakdownChart from './ScoreBreakdownChart';

export default function ExplainabilityPanel({ candidate }) {
  if (!candidate) {
    return (
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
        <h2 className="text-xl font-semibold text-slate-900">Candidate explainability</h2>
        <p className="mt-4 text-slate-600">Select a ranked candidate to see match drivers and scoring details.</p>
      </div>
    );
  }

  const breakdown = [
    { name: 'Role fit', score: candidate.skill_score || 0 },
    { name: 'Experience', score: candidate.experience_score || 0 },
    { name: 'Behavior', score: candidate.recruitability_score || 0 },
    { name: 'LLM signal', score: candidate.llm_score || 0 },
  ];

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-sky-600">Explainable match</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">{candidate.candidate?.full_name || 'Candidate'}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">{candidate.recruiter_summary || 'A balanced hybrid score from skills, experience, and behavioral signals.'}</p>
          </div>
          <div className="rounded-full bg-slate-900 px-5 py-3 text-lg font-semibold text-white">
            {Math.round(candidate.final_score)}%
          </div>
        </div>

        <div className="mt-6 space-y-4 text-sm text-slate-700">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-3xl bg-slate-50 p-4">
              <p className="text-slate-500">Skills</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{candidate.candidate?.skills || 'N/A'}</p>
            </div>
            <div className="rounded-3xl bg-slate-50 p-4">
              <p className="text-slate-500">Portfolio</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{candidate.candidate?.profile_text?.slice(0, 80) || 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
        <h3 className="text-lg font-semibold text-slate-900">Score breakdown</h3>
        <p className="mt-2 text-sm text-slate-600">This visualization shows why the candidate ranks highly.</p>
        <ScoreBreakdownChart data={breakdown} />
      </div>
    </div>
  );
}
