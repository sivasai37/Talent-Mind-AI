import { useEffect, useMemo, useState } from 'react';
import { analyzeJD, exportRankings, getCandidates, getRankings, rankCandidates } from './api';
import JobDescriptionUploader from './components/JobDescriptionUploader';
import RankingTable from './components/RankingTable';
import ExplainabilityPanel from './components/ExplainabilityPanel';

const defaultJob = {
  job_title: 'Senior Product Designer',
  job_description:
    'Design intuitive customer experiences for web and mobile. Collaborate with product, engineering, and research teams to own end-to-end design flows, user journeys, and cross-functional execution.',
};

function App() {
  const [jobTitle, setJobTitle] = useState(defaultJob.job_title);
  const [jobDescription, setJobDescription] = useState(defaultJob.job_description);
  const [summary, setSummary] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [selected, setSelected] = useState(null);
  const [latestJobId, setLatestJobId] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const topCandidate = useMemo(() => rankings[0] || null, [rankings]);

  useEffect(() => {
    getCandidates().then(setCandidates).catch(() => {});
    getRankings()
      .then((jobs) => {
        if (jobs && jobs.length > 0) {
          const latest = jobs[0];
          setLatestJobId(latest.id);
          setRankings(latest.results || []);
          setSelected(latest.results?.[0] || null);
        }
      })
      .catch(() => {});
  }, []);

  const handleAnalyze = async (title, description) => {
    setLoading(true);
    setError('');
    try {
      const data = await analyzeJD(title, description);
      setSummary(data);
    } catch (err) {
      setError(err.message || 'Unable to analyze job description');
    } finally {
      setLoading(false);
    }
  };

  const handleRank = async (payload) => {
    setLoading(true);
    setError('');
    try {
      const data = await rankCandidates(payload);
      setLatestJobId(data.id || null);
      setRankings(data.results || []);
      setSelected(data.results?.[0] || null);
    } catch (err) {
      setError(err.message || 'Ranking failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async ({ job_title, job_description, filters }) => {
    setJobTitle(job_title);
    setJobDescription(job_description);
    await handleAnalyze(job_title, job_description);
    await handleRank({ job_title, job_description, filters });
  };

  const selectedCandidate = selected || topCandidate;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 rounded-3xl bg-white p-8 shadow-sm shadow-slate-200">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-sky-600">TalentMind AI</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                Candidate Ranking Dashboard
              </h1>
              <p className="mt-2 max-w-2xl text-slate-600">
                Upload a job description, compare ranked candidates, and inspect score details with explainability.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <a
                href={latestJobId ? `${exportRankings()}?job_id=${latestJobId}` : '#'}
                className={`inline-flex items-center rounded-full border px-4 py-2 text-sm font-medium shadow-sm transition ${latestJobId ? 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50' : 'border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed'}`}
                aria-disabled={!latestJobId}
              >
                Export rankings CSV
              </a>
            </div>
          </div>
        </header>

        <main className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <section className="space-y-6">
            <JobDescriptionUploader
              jobTitle={jobTitle}
              jobDescription={jobDescription}
              loading={loading}
              onSubmit={handleSubmit}
            />

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
                <h2 className="text-xl font-semibold text-slate-900">Job summary</h2>
                <p className="mt-4 text-slate-600">Use this summary to validate candidate fit and hiring priorities.</p>
                <div className="mt-5 space-y-4 text-sm text-slate-700">
                  <div>
                    <span className="block font-semibold">Title</span>
                    <span>{jobTitle}</span>
                  </div>
                  <div>
                    <span className="block font-semibold">Top skills</span>
                    <span>{summary?.top_skills?.join(', ') || 'No summary yet'}</span>
                  </div>
                  <div>
                    <span className="block font-semibold">Experience focus</span>
                    <span>{summary?.experience_focus || 'Awaiting analysis'}</span>
                  </div>
                  <div>
                    <span className="block font-semibold">Behavioral themes</span>
                    <span>{summary?.behavioral_themes?.join(', ') || 'Awaiting analysis'}</span>
                  </div>
                </div>
              </div>

              <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
                <h2 className="text-xl font-semibold text-slate-900">Current ranking</h2>
                <p className="mt-4 text-slate-600">Candidates are ranked by hybrid match score, experience, and behavioral signals.</p>
                <div className="mt-5 flex items-center justify-between rounded-2xl bg-slate-50 p-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Best candidate</p>
                    <p className="mt-2 text-lg font-semibold text-slate-900">{selectedCandidate?.candidate?.full_name || 'No candidate selected'}</p>
                  </div>
                  <div className="rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-white">
                    {selectedCandidate ? `${Math.round(selectedCandidate.final_score)}%` : 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
              <h2 className="text-xl font-semibold text-slate-900">Ranked candidates</h2>
              <RankingTable
                rankings={rankings}
                onSelect={setSelected}
                selectedId={selectedCandidate?.candidate?.id}
              />
            </div>
          </section>

          <section className="space-y-6">
            <ExplainabilityPanel candidate={selectedCandidate} />
          </section>
        </main>

        {error ? (
          <div className="mt-6 rounded-3xl bg-rose-50 p-5 text-rose-700 shadow-sm shadow-rose-100">
            <p className="font-medium">Error</p>
            <p className="mt-2 text-sm">{error}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default App;
