// ExplainabilityPanel.jsx — Full HireGenius AI Candidate Intelligence Panel

import ScoreBreakdownChart from './ScoreBreakdownChart';
import RadarChart from './RadarChart';

function RiskBadge({ level }) {
  const config = {
    low: { label: 'Low Risk', color: 'var(--brand-success)', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)' },
    medium: { label: 'Medium Risk', color: 'var(--brand-warning)', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' },
    high: { label: 'High Risk', color: 'var(--brand-danger)', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' },
  };
  const c = config[level] || config.medium;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '5px',
      padding: '3px 10px', borderRadius: '999px',
      background: c.bg, border: `1px solid ${c.border}`,
      color: c.color, fontSize: '11px', fontWeight: '600',
    }}>
      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: c.color, flexShrink: 0 }} />
      {c.label}
    </span>
  );
}

function RecommendationBadge({ rec }) {
  const r = (rec || '').toLowerCase();
  const config = r.includes('strong')
    ? { color: 'var(--brand-success)', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)' }
    : r.includes('weak')
    ? { color: 'var(--brand-danger)', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' }
    : { color: 'var(--brand-warning)', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' };

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '5px',
      padding: '5px 14px', borderRadius: '999px',
      background: config.bg, border: `1px solid ${config.border}`,
      color: config.color, fontSize: '12px', fontWeight: '700',
    }}>
      {rec || 'Moderate Fit'}
    </span>
  );
}

function ScoreGauge({ value, size = 64, label }) {
  const pct = Math.min(100, Math.max(0, value || 0));
  const r = (size - 8) / 2;
  const circumference = 2 * Math.PI * r;
  const dash = (pct / 100) * circumference;
  const isHigh = pct >= 75;
  const isMed = pct >= 50;
  const color = isHigh ? '#10b981' : isMed ? '#6366f1' : '#f59e0b';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
          <circle
            cx={size/2} cy={size/2} r={r} fill="none"
            stroke={color} strokeWidth="6"
            strokeDasharray={`${dash} ${circumference}`}
            strokeLinecap="round"
            style={{ transition: 'stroke-dasharray 0.8s ease' }}
          />
        </svg>
        <div style={{
          position: 'absolute', inset: 0, display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          fontSize: '13px', fontWeight: '700', color,
        }}>
          {Math.round(pct)}
        </div>
      </div>
      {label && <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: '500' }}>{label}</span>}
    </div>
  );
}

export default function ExplainabilityPanel({ candidate, activeTab, onTabChange }) {
  if (!candidate) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="empty-state-icon">🧠</div>
          <div className="empty-state-title">Select a Candidate</div>
          <div className="empty-state-desc">
            Click any candidate in the ranking table to view their full AI-powered evaluation report.
          </div>
        </div>
      </div>
    );
  }

  const candidateName = candidate.candidate?.full_name || candidate.full_name || 'Candidate';
  const finalScore = Math.round(candidate.final_score || 0);
  const potentialScore = Math.round(candidate.potential_score || 0);
  const confidenceScore = Math.round(candidate.confidence_score || 0);
  const riskLevel = candidate.risk_level || 'medium';
  const recommendation = candidate.recruiter_recommendation || candidate.payload?.recruiter_ai?.recommendation || 'Moderate Fit';

  const breakdown = [
    { name: 'Skill Alignment', score: candidate.skill_score || 0 },
    { name: 'Experience Fit', score: candidate.experience_score || 0 },
    { name: 'Behavioral Score', score: candidate.recruitability_score || 0 },
    { name: 'AI/LLM Signal', score: candidate.llm_score || 0 },
    { name: 'Semantic Match', score: candidate.semantic_score || 0 },
  ];

  const strengths = candidate.strengths || [];
  const weaknesses = candidate.weaknesses || [];
  const matchingSkills = candidate.matching_skills || candidate.payload?.matching_skills || [];
  const missingSkills = candidate.missing_skills || candidate.payload?.missing_skills || [];
  const learningPath = candidate.learning_path || candidate.payload?.learning_path || [];
  const interviewQuestions = candidate.interview_questions || candidate.payload?.interview_questions || [];
  const futureRoles = candidate.future_roles || candidate.payload?.future_roles || [];
  const growthForecast = candidate.growth_forecast || candidate.payload?.growth_forecast || {};
  const salaryFit = candidate.salary_fit || candidate.payload?.salary_fit || {};
  const whySelected = candidate.why_selected || candidate.payload?.why_selected || '';
  const whyRejected = candidate.why_rejected || candidate.payload?.why_rejected || '';
  const roleFitAnalysis = candidate.role_fit_analysis || candidate.payload?.role_fit_analysis || '';
  const recruiterSummary = candidate.recruiter_summary || candidate.behaviour_summary || '';
  const careerGrowth = candidate.career_growth || candidate.payload?.career_growth || candidate.payload?.career_trajectory || '';
  const recruiterSignals = candidate.recruiter_signals || candidate.payload?.recruiter_signals || candidate.explanation?.recruiter_signals || {};
  const riskFactors = candidate.risk_factors || candidate.payload?.risk_factors || candidate.explanation?.risk_factors || [];
  const careerTrajectory = careerGrowth || candidate.payload?.career_trajectory || candidate.career_trajectory || 'ascending';

  const tabs = ['Overview', 'Scores', 'Gap Analysis', 'Interview', 'Growth'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header Card */}
      <div className="card" style={{
        background: 'linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%)',
        borderColor: 'var(--border-default)',
      }}>
        {/* Top row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '11px', color: 'var(--brand-primary)', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: '600' }}>
                HireGenius AI · Candidate Intelligence
              </span>
              <RiskBadge level={riskLevel} />
            </div>
            <h2 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '8px' }}>
              {candidateName}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
              <RecommendationBadge rec={recommendation} />
              {careerTrajectory && (
                <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  📈 {careerTrajectory.charAt(0).toUpperCase() + careerTrajectory.slice(1)} trajectory
                </span>
              )}
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', maxWidth: '480px' }}>
              {recruiterSummary || 'AI-powered candidate evaluation based on multi-agent analysis.'}
            </p>
          </div>

          {/* Score gauges */}
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <ScoreGauge value={finalScore} size={72} label="Final Score" />
            <ScoreGauge value={potentialScore} size={72} label="Potential" />
            <ScoreGauge value={confidenceScore} size={72} label="Confidence" />
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => onTabChange(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'Overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Why Selected / Why Rejected */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="card" style={{ background: 'rgba(16,185,129,0.06)', borderColor: 'rgba(16,185,129,0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <span style={{ fontSize: '16px' }}>✅</span>
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--brand-success)' }}>Why Selected</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                {whySelected || 'Strong alignment across key evaluation dimensions.'}
              </p>
            </div>
            <div className="card" style={{ background: 'rgba(239,68,68,0.06)', borderColor: 'rgba(239,68,68,0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                <span style={{ fontSize: '16px' }}>⚠️</span>
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--brand-danger)' }}>Risks / Gaps</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                {whyRejected || 'Review skill gaps and experience alignment before proceeding.'}
              </p>
            </div>
          </div>

          {/* Role Fit Analysis */}
          {roleFitAnalysis && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span style={{ fontSize: '16px' }}>🎯</span>
                <span style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>Role Fit Analysis</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.7' }}>{roleFitAnalysis}</p>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="card">
              <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                💪 Strengths
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {strengths.length > 0 ? strengths.map((s, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--brand-success)', marginTop: '2px', flexShrink: 0 }}>▸</span>
                    {s}
                  </div>
                )) : <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No specific strengths identified.</p>}
              </div>
            </div>
            <div className="card">
              <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                🔴 Weaknesses
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {weaknesses.length > 0 ? weaknesses.map((w, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--brand-danger)', marginTop: '2px', flexShrink: 0 }}>▸</span>
                    {w}
                  </div>
                )) : <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No significant weaknesses flagged.</p>}
              </div>
            </div>
          </div>

          {(matchingSkills.length > 0 || riskFactors.length > 0) && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="card">
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px' }}>
                  Matching Skills
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {matchingSkills.length > 0 ? matchingSkills.map((skill, i) => (
                    <span key={i} className="skill-chip skill-chip-match">{skill.replace(/_/g, ' ')}</span>
                  )) : <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Partial overlap only.</span>}
                </div>
              </div>
              <div className="card">
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px' }}>
                  Risk Factors
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {riskFactors.length > 0 ? riskFactors.map((risk, i) => (
                    <div key={i} style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>• {risk}</div>
                  )) : <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No major risks flagged.</span>}
                </div>
              </div>
            </div>
          )}

          {Object.keys(recruiterSignals).length > 0 && (
            <div className="card">
              <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px' }}>
                Recruiter Signals
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
                {recruiterSignals.response_rate != null && (
                  <div className="metric-pill"><span>Response rate</span><strong>{Math.round(recruiterSignals.response_rate * 100)}%</strong></div>
                )}
                {recruiterSignals.saved_by_recruiters_30d != null && (
                  <div className="metric-pill"><span>Saved (30d)</span><strong>{recruiterSignals.saved_by_recruiters_30d}</strong></div>
                )}
                {recruiterSignals.search_appearance_30d != null && (
                  <div className="metric-pill"><span>Search views (30d)</span><strong>{recruiterSignals.search_appearance_30d}</strong></div>
                )}
                {recruiterSignals.notice_period_days != null && (
                  <div className="metric-pill"><span>Notice period</span><strong>{recruiterSignals.notice_period_days}d</strong></div>
                )}
              </div>
            </div>
          )}

          {careerGrowth && (
            <div className="card">
              <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Career Growth</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>{careerGrowth}</p>
            </div>
          )}

          {/* Radar Chart */}
          <div className="card">
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              📊 Candidate vs Job Radar
            </div>
            <RadarChart candidate={candidate} />
          </div>
        </div>
      )}

      {activeTab === 'Scores' && (
        <div className="card">
          <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '4px' }}>Score Breakdown</div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Multi-dimensional evaluation across 5 intelligence layers.
          </p>
          <ScoreBreakdownChart data={breakdown} />

          {/* Score explanations */}
          <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              { label: '🧩 Skill Alignment', text: candidate.skill_explanation || candidate.payload?.skill_explanation || '' },
              { label: '📋 Experience', text: candidate.experience_explanation || candidate.payload?.experience_explanation || '' },
              { label: '🤝 Behavioral', text: candidate.behavioral_explanation || candidate.payload?.behavioral_explanation || '' },
              { label: '🤖 Semantic', text: candidate.semantic_explanation || candidate.payload?.semantic_explanation || '' },
            ].filter(e => e.text).map((e, i) => (
              <div key={i} style={{ padding: '12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-accent)', marginBottom: '6px' }}>{e.label}</div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.6' }}>{e.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'Gap Analysis' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Missing Skills */}
          <div className="card">
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🔍 Missing Skills
            </div>
            {missingSkills.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {missingSkills.map((skill, i) => (
                  <span key={i} className="skill-tag skill-tag-missing">
                    ✗ {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '13px', color: 'var(--brand-success)' }}>✓ All required skills are present!</p>
            )}
          </div>

          {/* Learning Path */}
          <div className="card">
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              📚 Recommended Learning Path
            </div>
            {learningPath.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {learningPath.map((item, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', padding: '10px 12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <span style={{
                      width: '22px', height: '22px', borderRadius: '50%',
                      background: 'var(--gradient-brand)', color: 'white',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '11px', fontWeight: '700', flexShrink: 0, marginTop: '1px',
                    }}>
                      {i + 1}
                    </span>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{item}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No learning path generated yet.</p>
            )}
          </div>

          {/* Salary Fit */}
          {(salaryFit.alignment || salaryFit.notes) && (
            <div className="card">
              <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                💰 Salary Fit Analysis
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <span className={`badge ${
                  salaryFit.alignment === 'aligned' ? 'badge-success' :
                  salaryFit.alignment === 'above_range' ? 'badge-danger' :
                  salaryFit.alignment === 'below_range' ? 'badge-warning' : 'badge-neutral'
                }`}>
                  {salaryFit.alignment || 'Unknown'}
                </span>
              </div>
              {salaryFit.notes && (
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>{salaryFit.notes}</p>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'Interview' && (
        <div className="card">
          <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🎙️ AI-Generated Interview Questions
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Tailored questions based on candidate profile and identified gaps.
          </p>
          {interviewQuestions.length > 0 ? (
            <div>
              {interviewQuestions.map((q, i) => (
                <div key={i} className="question-item">
                  <span className="question-number">{i + 1}</span>
                  <p className="question-text">{q}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '32px 20px' }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>🎙️</div>
              <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Interview questions will appear after ranking.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'Growth' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Future Roles */}
          {futureRoles.length > 0 && (
            <div className="card">
              <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🚀 Future Role Predictions
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {futureRoles.map((role, i) => (
                  <div key={i} style={{
                    padding: '8px 16px', borderRadius: 'var(--radius-full)',
                    background: 'rgba(99,102,241,0.1)', border: '1px solid var(--border-default)',
                    color: 'var(--text-accent)', fontSize: '13px', fontWeight: '500',
                    display: 'flex', alignItems: 'center', gap: '6px',
                  }}>
                    <span style={{ color: 'var(--brand-primary)' }}>→</span> {role}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Growth Forecast */}
          {Object.keys(growthForecast).length > 0 && (
            <div className="card">
              <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                📈 1–3 Year Growth Forecast
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(growthForecast).map(([period, prediction], i) => (
                  <div key={i} style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                    <div style={{
                      minWidth: '52px', height: '52px', borderRadius: 'var(--radius-md)',
                      background: 'var(--gradient-brand)', color: 'white',
                      display: 'flex', flexDirection: 'column', alignItems: 'center',
                      justifyContent: 'center', fontSize: '10px', fontWeight: '700',
                      textAlign: 'center', padding: '4px',
                    }}>
                      {period.replace('year_', 'Yr ')}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', paddingTop: '12px' }}>
                        {prediction}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Candidate profile quick view */}
          <div className="card">
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '12px' }}>
              👤 Candidate Profile
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '13px' }}>
              <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>Skills</div>
                <div style={{ color: 'var(--text-primary)', fontWeight: '500' }}>
                  {candidate.candidate?.skills ? candidate.candidate.skills.split(',').slice(0, 4).join(', ') : 'N/A'}
                </div>
              </div>
              <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>Experience</div>
                <div style={{ color: 'var(--text-primary)', fontWeight: '500' }}>
                  {candidate.candidate?.years_experience || 0} years
                </div>
              </div>
              <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>GitHub</div>
                <div style={{ color: 'var(--text-primary)', fontWeight: '500' }}>
                  {candidate.candidate?.github_url ? (
                    <a href={candidate.candidate.github_url} target="_blank" rel="noopener noreferrer"
                      style={{ color: 'var(--brand-primary)', textDecoration: 'none' }}>
                      View Profile
                    </a>
                  ) : 'Not provided'}
                </div>
              </div>
              <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>Open to Work</div>
                <div style={{ color: candidate.candidate?.open_to_work ? 'var(--brand-success)' : 'var(--text-muted)', fontWeight: '500' }}>
                  {candidate.candidate?.open_to_work ? '✓ Yes' : '✗ No'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
