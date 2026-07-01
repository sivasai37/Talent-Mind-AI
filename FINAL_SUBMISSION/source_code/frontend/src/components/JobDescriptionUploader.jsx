import { useState } from 'react';

export default function JobDescriptionUploader({ jobTitle, jobDescription, loading, onSubmit }) {
  const [title, setTitle] = useState(jobTitle);
  const [description, setDescription] = useState(jobDescription);
  const [filters, setFilters] = useState({ location: '', level: '' });

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({ job_title: title, job_description: description, filters });
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-sky-600">Job description</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Analyze and rank candidates</h2>
          <p className="mt-2 text-slate-600">Paste the job description and submit to see ranking insights instantly.</p>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center rounded-full bg-sky-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {loading ? 'Working…' : 'Analyze & Rank'}
        </button>
      </div>

      <div className="mt-8 space-y-5">
        <div>
          <label className="text-sm font-medium text-slate-700">Job title</label>
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
            placeholder="Senior Product Designer"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-slate-700">Job description</label>
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            rows={8}
            className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
            placeholder="Enter the full job description here..."
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-sm font-medium text-slate-700">Desired location</label>
            <input
              value={filters.location}
              onChange={(event) => setFilters((prev) => ({ ...prev, location: event.target.value }))}
              className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
              placeholder="Remote, US, Europe"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Seniority level</label>
            <input
              value={filters.level}
              onChange={(event) => setFilters((prev) => ({ ...prev, level: event.target.value }))}
              className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
              placeholder="Senior, Lead, Manager"
            />
          </div>
        </div>
      </div>
    </form>
  );
}
