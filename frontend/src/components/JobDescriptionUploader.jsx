// JobDescriptionUploader.jsx — HireGenius AI JD Input & Controls

import { useState } from 'react';

const EXAMPLE_JDS = [
  {
    title: 'Senior Backend Engineer',
    description: `We are looking for a Senior Backend Engineer to join our platform team.

Required Skills: Python, Django, PostgreSQL, Redis, Docker, Kubernetes, REST API design
Nice to have: GraphQL, Kafka, AWS, Terraform

Requirements:
- 5+ years of backend development experience
- Strong understanding of distributed systems and microservices
- Experience with CI/CD pipelines and DevOps practices
- Leadership experience mentoring junior engineers

Behavioral expectations: ownership mindset, strong communication, collaborative team player`
  },
  {
    title: 'ML Research Engineer',
    description: `We are hiring an ML Research Engineer to advance our AI capabilities.

Required Skills: Python, PyTorch, TensorFlow, NLP, LLMs, Machine Learning, Deep Learning
Nice to have: Reinforcement Learning, MLOps, Kubernetes, RLHF

Requirements:
- PhD or 4+ years in ML/AI research
- Publications in top-tier venues (NeurIPS, ICML, ACL) preferred
- Strong math background: linear algebra, probability, optimization

Behavioral: research-driven mindset, intellectual curiosity, collaborative`
  },
  {
    title: 'Engineering Manager',
    description: `We seek an Engineering Manager to lead a cross-functional engineering team.

Required Skills: People management, Agile, System design, Technical leadership, Roadmap planning
Nice to have: Backend engineering, Data engineering, OKR framework

Requirements:
- 8+ years engineering, with 3+ years in management
- Track record of growing high-performing teams
- Excellent stakeholder communication and executive presence

Behavioral expectations: strong leadership, empathy, data-driven decision making`
  },
];

export default function JobDescriptionUploader({ jobTitle, jobDescription, loading, onSubmit, rankings = [], onExportExcel, latestJobId }) {
  const [title, setTitle] = useState(jobTitle || '');
  const [description, setDescription] = useState(jobDescription || '');
  const [topK, setTopK] = useState(10);
  const [showExamples, setShowExamples] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!description.trim()) return;
    onSubmit({ job_title: title, job_description: description, top_k: topK });
  };

  const loadExample = (example) => {
    setTitle(example.title);
    setDescription(example.description);
    setShowExamples(false);
  };

  const charCount = description.length;
  const charLimit = 20000;

  return (
    <form onSubmit={handleSubmit} className="card">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap', marginBottom: '24px' }}>
        <div>
          <p style={{ fontSize: '11px', color: 'var(--brand-primary)', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: '600', marginBottom: '6px' }}>
            Job Intelligence Engine
          </p>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '6px' }}>
            Analyze & Rank Candidates
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Paste a job description to activate AI-powered multi-agent ranking.
          </p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setShowExamples(!showExamples)}
            >
              📋 Examples
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !description.trim()}
              id="analyze-rank-btn"
            >
              {loading ? (
                <>
                  <span className="spin">⟳</span>
                  Ranking…
                </>
              ) : (
                <>
                  ⚡ Analyze & Rank
                </>
              )}
            </button>
            {latestJobId && (
              <button
                type="button"
                className="btn btn-secondary"
                disabled={rankings.length === 0}
                onClick={onExportExcel}
                id="export-excel-btn"
              >
                📥 Export Results (.xlsx)
              </button>
            )}
          </div>
          {latestJobId && rankings.length === 0 && (
            <span style={{ fontSize: '12px', color: 'var(--brand-danger)', fontWeight: '500' }}>
              No ranked candidates available to export.
            </span>
          )}
        </div>
      </div>

      {/* Example JDs */}
      {showExamples && (
        <div style={{
          padding: '12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)', marginBottom: '20px',
          display: 'flex', flexDirection: 'column', gap: '6px',
        }}>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Load an example job description:</p>
          {EXAMPLE_JDS.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => loadExample(ex)}
              style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                padding: '10px 12px', background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)',
                color: 'var(--text-secondary)', fontSize: '13px', cursor: 'pointer',
                transition: 'var(--transition-fast)', fontFamily: 'inherit', textAlign: 'left',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--brand-primary)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
            >
              <span style={{ fontSize: '16px' }}>
                {i === 0 ? '⚙️' : i === 1 ? '🔬' : '👥'}
              </span>
              <div>
                <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{ex.title}</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {ex.description.slice(0, 80)}...
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Form Fields */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Job Title */}
        <div className="form-group">
          <label className="form-label">Job Title</label>
          <input
            id="job-title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="form-input"
            placeholder="e.g. Senior Backend Engineer, ML Research Scientist..."
          />
        </div>

        {/* Job Description */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="form-label">Job Description</label>
            <span style={{ fontSize: '11px', color: charCount > charLimit * 0.9 ? 'var(--brand-danger)' : 'var(--text-muted)' }}>
              {charCount.toLocaleString()} / {charLimit.toLocaleString()} chars
            </span>
          </div>
          <textarea
            id="job-description-input"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={9}
            className="form-input form-textarea"
            placeholder="Paste the full job description here. Include required skills, experience requirements, and behavioral expectations for best results..."
          />
        </div>

        {/* Bottom row: filters + top K */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 120px', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label">Location Filter</label>
            <input
              className="form-input"
              placeholder="Remote, US, Europe..."
            />
          </div>
          <div className="form-group">
            <label className="form-label">Seniority Level</label>
            <input
              className="form-input"
              placeholder="Senior, Lead, Manager..."
            />
          </div>
          <div className="form-group">
            <label className="form-label">Top K Results</label>
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="form-input"
              id="top-k-select"
            >
              {[10, 25, 50, 100].map(k => (
                <option key={k} value={k}>{k} candidates</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Info bar */}
      <div style={{
        marginTop: '20px', padding: '10px 14px', background: 'rgba(99,102,241,0.06)',
        border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)',
        display: 'flex', alignItems: 'center', gap: '10px',
      }}>
        <span style={{ fontSize: '14px' }}>ℹ️</span>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.5' }}>
          HireGenius AI auto-detects role type and applies dynamic weights.
          5 specialized agents evaluate skill fit, experience, behavior, recruitability, and generate a hiring consensus.
        </p>
      </div>
    </form>
  );
}
