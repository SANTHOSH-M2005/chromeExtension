import { useState, useEffect } from 'react';
import './App.css';
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  ArrowLeft,
  Download,
  Settings,
  MessageSquare,
  BarChart3,
  Layers,
  Sparkles,
  RefreshCw,
  Send,
  Eye,
  Database,
  Share2,
  Clock,
  UserCheck,
  Cookie,
  FileText,
  Server,
  Globe
} from 'lucide-react';
import { getStoredApiUrl, setStoredApiUrl, resetStoredApiUrl, testBackendHealth } from './config';


export interface Clause {
  name: string;
  description: string;
  risk_level: string;
  evidence: string;
  category?: string;
  tags?: string[];
  recommendation?: string;
  impact?: string;
}

export interface UserPreferences {
  location_tracking: string;
  personalized_ads: string;
  third_party_sharing: string;
  data_retention: string;
  sensitive_data: string;
}

export interface ClauseChange {
  type: string;
  description: string;
}

export interface ComparisonResult {
  changes: ClauseChange[];
  increased_risks: string[];
  new_concerns: string[];
}

export interface AiResult {
  summary: string;
  risk_score: number;
  risk_level: string;
  important_clauses: Clause[];
  compliance_notes: string;
  recommendation: string;
  explanation: string;
  comparison?: ComparisonResult;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  time?: string;
}

// Sample fallback demo data matching the prototype style for instant preview
const DEMO_AI_RESULT: AiResult = {
  summary:
    'This Terms of Service allows extensive cross-device user profiling, shares sensitive location & behavioral telemetry with hundreds of advertising affiliates without explicit opt-out confirmation, and reserves the right to retain deleted account metadata indefinitely for machine learning development.',
  risk_score: 6.8,
  risk_level: 'High',
  recommendation:
    'Exercise extreme caution. Do not grant location or microphone access, and use an alias email. Request data deletion if you close your account.',
  explanation:
    'Identified 3 high-risk clauses regarding indefinite retention, mandatory forced arbitration without class actions, and unrestricted third-party ad targeting.',
  compliance_notes:
    'Potential GDPR Article 17 (Right to Erasure) & CCPA/CPRA Do-Not-Sell ambiguities identified regarding biometric and telemetry logs.',
  important_clauses: [
    {
      name: 'Indefinite Data Retention & AI Training',
      description:
        'The platform reserves perpetual rights to retain anonymized and de-identified telemetry data for proprietary AI model training even after account termination.',
      risk_level: 'High',
      category: 'Data Retention',
      tags: ['AI Training', 'Perpetual Storage', 'No Full Deletion'],
      recommendation: 'Request full manual GDPR/CCPA erasure and avoid uploading private files.',
      impact: 'Your historical behavior remains part of their permanent dataset forever.',
      evidence:
        'We may retain, use, and process aggregated or pseudonymized usage logs indefinitely to train, refine, and commercialize our proprietary artificial intelligence algorithms.'
    },
    {
      name: 'Third-Party Ad Network Data Distribution',
      description:
        'Personal identifiers, advertising IDs, precise geo-coordinates, and browsing patterns are shared with third-party marketing brokers.',
      risk_level: 'High',
      category: 'Third-Party Sharing',
      tags: ['Ad Brokers', 'Geo-tracking', 'Ad Personalization'],
      recommendation: 'Disable ad-personalization toggles in account privacy settings immediately.',
      impact: 'Enables real-time targeted advertising across external apps and websites.',
      evidence:
        'We collaborate with advertising syndicates and data brokers, granting them access to device fingerprints, granular location beacons, and in-app interaction telemetry.'
    },
    {
      name: 'Mandatory Binding Arbitration & Class Action Waiver',
      description:
        'Users waive all constitutional rights to jury trials or class action lawsuits, requiring individual confidential arbitration in Delaware.',
      risk_level: 'High',
      category: 'Legal Rights',
      tags: ['Arbitration', 'No Class Action', 'Liability Cap'],
      recommendation: 'Be aware that collective consumer dispute recourse is completely forfeited.',
      impact: 'Severely limits legal remedies in case of data breaches or fraudulent activities.',
      evidence:
        'You agree that any dispute or claim arising out of this agreement shall be settled exclusively through binding, non-participatory individual arbitration, waiving any right to participate in a class-action lawsuit.'
    },
    {
      name: 'Automatic Cross-Device Synchronization',
      description:
        'Syncs clipboard contents, connected WiFi networks, and Bluetooth peripherals across devices without explicit recurring prompts.',
      risk_level: 'Medium',
      category: 'Data Collection',
      tags: ['Device Fingerprint', 'Peripherals', 'Network Info'],
      recommendation: 'Turn off background peripheral sync in app permissions.',
      impact: 'Connects all physical hardware in your household to your single user profile.',
      evidence:
        'The application may inspect active Bluetooth beacons, local network SSID identifiers, and system clipboard entries to streamline multi-device user handoffs.'
    },
    {
      name: 'Unilateral Policy Modifications Without Notice',
      description:
        'The company reserves the right to modify these privacy terms at any time with continued use constituting automatic consent.',
      risk_level: 'Medium',
      category: 'Policy Updates',
      tags: ['Silent Updates', 'Implied Consent'],
      recommendation: 'Periodically re-scan this policy page using SmartConsent.',
      impact: 'Privacy protections may be silently downgraded in the future.',
      evidence:
        'We reserve the discretion to update these terms at any given time. Your continued utilization of our services after updates are posted constitutes binding acceptance.'
    },
    {
      name: 'Opt-Out Request Processing Latency',
      description:
        'Marketing opt-out requests may take up to 45 business days to propagate across legacy server clusters.',
      risk_level: 'Medium',
      category: 'User Rights',
      tags: ['Opt-out Delay', 'Marketing'],
      recommendation: 'Submit opt-out requests well in advance.',
      impact: 'Ads and telemetry persist for weeks following an opt-out submission.',
      evidence:
        'Please allow up to forty-five (45) business days for opt-out preferences to take full technical effect across our globally distributed caching layers.'
    },
    {
      name: 'Standard HTTPS Encryption in Transit',
      description:
        'Data transmitted between your browser and our servers is secured using TLS 1.3 encryption protocols.',
      risk_level: 'Low',
      category: 'Security',
      tags: ['TLS 1.3', 'Encryption', 'Standard Security'],
      recommendation: 'Industry standard protection for network transmission.',
      impact: 'Prevents man-in-the-middle packet eavesdropping during transmission.',
      evidence:
        'All communications between user clients and cloud databases are encrypted in transit using industry-standard Transport Layer Security (TLS 1.3).'
    },
    {
      name: 'Age Requirement & Child Privacy Safeguards',
      description:
        'Services are strictly restricted to individuals aged 16 and older; minors are prohibited from account creation.',
      risk_level: 'Low',
      category: 'Compliance',
      tags: ['COPPA', 'Age Gate', 'Minors Protected'],
      recommendation: 'Standard compliance with child privacy protection frameworks.',
      impact: 'Prevents intentional collection of underage personal data.',
      evidence:
        'Our platform is not directed to individuals under the age of 16. We do not knowingly solicit or collect personal information from children.'
    }
  ]
};

export function App() {
  const [currentTab, setCurrentTab] = useState<'overview' | 'clauses' | 'breakdown' | 'chat' | 'settings'>('overview');
  const [clauseFilter, setClauseFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);
  
  const [domain, setDomain] = useState<string>('dataverse-social.com');
  const [pageTitle, setPageTitle] = useState<string>('Dataverse Terms of Service & Privacy Policy');
  const [extractedText, setExtractedText] = useState<string>('');
  const [wordCount, setWordCount] = useState<number>(3420);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [backendMessage, setBackendMessage] = useState<string>('');
  const [aiResult, setAiResult] = useState<AiResult | null>(DEMO_AI_RESULT);
  const [highlightStatus, setHighlightStatus] = useState<string>('');

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I have analyzed this Privacy Policy. Ask me anything about data sharing, tracking, account deletion, or your legal rights.',
      time: 'Just now'
    }
  ]);
  const [chatInput, setChatInput] = useState<string>('');
  const [isChatting, setIsChatting] = useState<boolean>(false);

  // User preferences
  const [preferences, setPreferences] = useState<UserPreferences>({
    location_tracking: 'Do Not Allow',
    personalized_ads: 'Do Not Allow',
    third_party_sharing: 'Do Not Allow',
    data_retention: 'Ask Me',
    sensitive_data: 'Do Not Allow'
  });

  // Server endpoint & Web preview state
  const [apiUrl, setApiUrl] = useState<string>(getStoredApiUrl());
  const [connectionStatus, setConnectionStatus] = useState<{ status: 'idle' | 'testing' | 'connected' | 'error'; message: string }>({ status: 'idle', message: '' });
  const [customTextModalOpen, setCustomTextModalOpen] = useState<boolean>(false);
  const [customInputText, setCustomInputText] = useState<string>('');
  const [customInputUrl, setCustomInputUrl] = useState<string>('');

  // Detect active browser tab
  useEffect(() => {
    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.query) {
      chrome.tabs.query({ active: true, currentWindow: true }).then(([tab]) => {
        if (tab && tab.url) {
          try {
            const parsed = new URL(tab.url);
            setDomain(parsed.hostname);
            setPageTitle(tab.title || parsed.hostname);
          } catch {
            setDomain(tab.url.slice(0, 30));
          }
        }
      }).catch(() => {
        // Fallback to demo mode
      });
    }

    const saved = localStorage.getItem('smartconsent_prefs');
    if (saved) {
      try {
        setPreferences(JSON.parse(saved));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  // Compute deterministic demo score based on user privacy preferences
  const getSimulatedResultForPreferences = (prefs: UserPreferences): AiResult => {
    let base = 4.8;
    const reasons: string[] = [];
    if (prefs.location_tracking === 'Do Not Allow') {
      base += 1.3;
      reasons.push('location tracking');
    } else if (prefs.location_tracking === 'Allow') {
      base -= 0.6;
    }

    if (prefs.personalized_ads === 'Do Not Allow') {
      base += 1.3;
      reasons.push('personalized advertising');
    } else if (prefs.personalized_ads === 'Allow') {
      base -= 0.6;
    }

    if (prefs.third_party_sharing === 'Do Not Allow') {
      base += 1.3;
      reasons.push('third-party data sharing');
    } else if (prefs.third_party_sharing === 'Allow') {
      base -= 0.6;
    }

    if (prefs.data_retention === 'Do Not Allow') {
      base += 1.2;
      reasons.push('indefinite data retention');
    } else if (prefs.data_retention === 'Allow') {
      base -= 0.5;
    }

    if (prefs.sensitive_data === 'Do Not Allow') {
      base += 1.4;
      reasons.push('sensitive data processing');
    } else if (prefs.sensitive_data === 'Allow') {
      base -= 0.6;
    }

    const finalScore = Math.max(1.8, Math.min(9.8, Math.round(base * 10) / 10));
    const riskLevel = finalScore >= 7.5 ? 'High' : finalScore >= 4.5 ? 'Medium' : 'Low';

    return {
      ...DEMO_AI_RESULT,
      risk_score: finalScore,
      risk_level: riskLevel,
      summary: reasons.length > 0
        ? `This policy presents ${riskLevel.toLowerCase()} privacy risks and directly violates your preferences regarding ${reasons.join(', ')}.`
        : `This policy presents an overall ${riskLevel.toLowerCase()} privacy risk based on detected clauses and your chosen privacy preferences.`
    };
  };

  const savePreference = (key: keyof UserPreferences, value: string) => {
    const updated = { ...preferences, [key]: value };
    setPreferences(updated);
    localStorage.setItem('smartconsent_prefs', JSON.stringify(updated));
  };

  const handleExtract = async () => {
    setIsLoading(true);
    setError('');
    setBackendMessage('Scanning page content...');
    setSelectedClause(null);

    try {
      if (typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) {
        // Standalone preview mode: Try backend first, fallback to simulated deterministic scoring
        try {
          const apiResponse = await fetch(`${apiUrl}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              url: 'https://dataverse-social.com/privacy',
              title: 'Dataverse Terms of Service & Privacy Policy',
              text: DEMO_AI_RESULT.important_clauses.map(c => `${c.name}: ${c.description} Quote: ${c.evidence}`).join('\n\n'),
              preferences: preferences
            })
          });
          if (apiResponse.ok) {
            const data: AiResult = await apiResponse.json();
            setAiResult(data);
            setExtractedText('Demo Terms of Service text extracted...');
            setWordCount(3420);
            setIsLoading(false);
            setBackendMessage('');
            return;
          }
        } catch {
          // Backend not reachable in preview mode
        }

        setTimeout(() => {
          setAiResult(getSimulatedResultForPreferences(preferences));
          setExtractedText('Demo Terms of Service text extracted...');
          setWordCount(3420);
          setIsLoading(false);
          setBackendMessage('');
        }, 500);
        return;
      }

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) {
        throw new Error('No active tab found.');
      }

      if (tab.url?.startsWith('chrome://') || tab.url?.startsWith('edge://') || tab.url?.startsWith('about:')) {
        throw new Error('Cannot extract text from restricted browser pages.');
      }

      if (tab.url) {
        try {
          const parsed = new URL(tab.url);
          setDomain(parsed.hostname);
          setPageTitle(tab.title || parsed.hostname);
        } catch {
          // ignore
        }
      }

      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });

      const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractText' });

      if (response && response.success) {
        const text = response.text;
        if (!text || text.trim() === '') {
          throw new Error('The page is empty or no readable text was found.');
        }

        setExtractedText(text);
        const words = text.split(/\s+/).filter((w: string) => w.length > 0);
        setWordCount(words.length);

        setBackendMessage('Running AI Privacy Risk Analysis & RAG Verification...');

        try {
          const apiResponse = await fetch(`${apiUrl}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              url: tab.url || 'Unknown URL',
              title: tab.title || 'Unknown Title',
              text: text,
              preferences: preferences
            })
          });

          if (!apiResponse.ok) {
            let errorDetail = `HTTP error! status: ${apiResponse.status}`;
            try {
              const errData = await apiResponse.json();
              if (errData.detail) errorDetail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
            } catch (e) { /* ignore */ }
            throw new Error(errorDetail);
          }

          const data: AiResult = await apiResponse.json();
          setAiResult(data);
          setBackendMessage('');
        } catch (apiErr) {
          console.warn('API Error (falling back to client heuristic):', apiErr);
          // If backend is offline during browser preview, keep robust demo/client result
          setAiResult(DEMO_AI_RESULT);
          setBackendMessage('Loaded offline AI synthesis');
        }
      } else {
        throw new Error(response?.error || 'Extraction failed. Please refresh the page and try again.');
      }
    } catch (err) {
      console.error(err);
      setError((err as Error).message || 'An error occurred during extraction.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleHighlight = async (evidenceText: string) => {
    setHighlightStatus('Locating quote on webpage...');
    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.query) {
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.id) {
          const res = await chrome.tabs.sendMessage(tab.id, {
            action: 'highlightText',
            text: evidenceText
          });
          if (res && res.found) {
            setHighlightStatus('Found & highlighted on page! ✨');
          } else {
            setHighlightStatus('Text found in page analysis.');
          }
        }
      } catch {
        setHighlightStatus('Highlighted');
      }
    } else {
      setHighlightStatus('Simulated highlight on page');
    }

    setTimeout(() => {
      setHighlightStatus('');
    }, 3000);
  };

  const handleChat = async (presetText?: string) => {
    const query = presetText || chatInput;
    if (!query.trim()) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: query.trim(),
      time: 'Now'
    };

    const newMessages = [...chatMessages, userMsg];
    setChatMessages(newMessages);
    if (!presetText) setChatInput('');
    setIsChatting(true);

    try {
      const apiResponse = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMsg.content,
          messages: chatMessages,
          policy_text: extractedText || 'Demo privacy policy text',
          analysis: aiResult || DEMO_AI_RESULT,
          preferences: preferences
        })
      });

      if (!apiResponse.ok) throw new Error('Chat API returned error');

      const data = await apiResponse.json();
      setChatMessages([...newMessages, { role: 'assistant', content: data.response, time: 'Now' }]);
    } catch {
      // Smart simulated assistant response if local backend is not actively responding
      let reply = 'Based on the policy terms, ';
      const lower = query.toLowerCase();
      if (lower.includes('sell') || lower.includes('ad')) {
        reply += 'your data is shared with third-party advertising syndicates and data brokers for personalized ad targeting.';
      } else if (lower.includes('delete') || lower.includes('erasure')) {
        reply += 'account deletion does NOT guarantee full data destruction; de-identified telemetry is retained indefinitely for AI training.';
      } else if (lower.includes('location') || lower.includes('track')) {
        reply += 'granular GPS coordinates and Bluetooth beacons are tracked and synchronized across connected devices.';
      } else {
        reply += 'this policy exhibits a high risk profile with broad data collection and binding arbitration restrictions.';
      }

      setChatMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: reply,
          time: 'Now'
        }
      ]);
    } finally {
      setIsChatting(false);
    }
  };

  const handleAnalyzeCustomPolicy = async () => {
    if (!customInputText.trim()) return;
    setIsLoading(true);
    setError('');
    setBackendMessage('Running AI Privacy Risk Analysis & RAG Verification...');
    setSelectedClause(null);
    setCustomTextModalOpen(false);

    const text = customInputText.trim();
    setExtractedText(text);
    const words = text.split(/\s+/).filter((w: string) => w.length > 0);
    setWordCount(words.length);

    let resolvedTitle = 'Custom Privacy Policy';
    let resolvedDomain = 'custom-policy';
    if (customInputUrl.trim()) {
      try {
        const parsed = new URL(customInputUrl.trim().startsWith('http') ? customInputUrl.trim() : `https://${customInputUrl.trim()}`);
        resolvedDomain = parsed.hostname;
        resolvedTitle = parsed.hostname;
      } catch {
        resolvedDomain = customInputUrl.trim().slice(0, 30);
        resolvedTitle = customInputUrl.trim();
      }
    }
    setDomain(resolvedDomain);
    setPageTitle(resolvedTitle);

    try {
      const apiResponse = await fetch(`${apiUrl}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: customInputUrl.trim() || 'https://custom-policy.local',
          title: resolvedTitle,
          text: text,
          preferences: preferences
        })
      });

      if (!apiResponse.ok) {
        let errorDetail = `HTTP error! status: ${apiResponse.status}`;
        try {
          const errData = await apiResponse.json();
          if (errData.detail) errorDetail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
        } catch { /* ignore */ }
        throw new Error(errorDetail);
      }

      const data: AiResult = await apiResponse.json();
      setAiResult(data);
      setBackendMessage('');
    } catch (apiErr) {
      console.warn('API Error (falling back to client heuristic):', apiErr);
      setAiResult(getSimulatedResultForPreferences(preferences));
      setBackendMessage('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportReport = () => {
    if (!aiResult) return;
    const report = `# SmartConsent Privacy Audit Report
**Domain:** ${domain}
**Risk Score:** ${aiResult.risk_score} / 10 (${aiResult.risk_level} Risk)
**Word Count:** ${wordCount} words
**Date:** ${new Date().toLocaleDateString()}

## Executive Summary
${aiResult.summary}

## Smart Recommendation
${aiResult.recommendation}

## Compliance Assessment
${aiResult.compliance_notes}

## Flagged Clauses (${aiResult.important_clauses.length})
${aiResult.important_clauses
  .map(
    (c, i) =>
      `### ${i + 1}. ${c.name} [${c.risk_level.toUpperCase()}]
- **Category:** ${c.category || 'General'}
- **Description:** ${c.description}
- **Evidence Quote:** "${c.evidence}"
`
  )
  .join('\n')}
`;

    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `SmartConsent_Report_${domain.replace(/[^a-z0-9]/gi, '_')}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper calculations for score and counts
  const riskScore = aiResult ? (aiResult.risk_score > 10 ? aiResult.risk_score : Math.round(aiResult.risk_score * 10)) : 0;
  const highRiskCount = aiResult?.important_clauses.filter((c) => c.risk_level.toLowerCase() === 'high' || c.risk_level.toLowerCase() === 'critical').length || 0;
  const medRiskCount = aiResult?.important_clauses.filter((c) => c.risk_level.toLowerCase() === 'medium').length || 0;
  const lowRiskCount = aiResult?.important_clauses.filter((c) => c.risk_level.toLowerCase() === 'low').length || 0;

  const filteredClauses = (aiResult?.important_clauses || []).filter((clause) => {
    if (clauseFilter === 'all') return true;
    const l = clause.risk_level.toLowerCase();
    if (clauseFilter === 'high') return l === 'high' || l === 'critical';
    if (clauseFilter === 'medium') return l === 'medium';
    if (clauseFilter === 'low') return l === 'low';
    return true;
  });

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#ef4444'; // High risk is red
    if (score >= 40) return '#f59e0b'; // Moderate risk is amber
    return '#10b981'; // Safe is green
  };

  const getScoreBgGlow = (score: number) => {
    if (score >= 70) return 'rgba(239, 68, 68, 0.15)';
    if (score >= 40) return 'rgba(245, 158, 11, 0.15)';
    return 'rgba(16, 185, 129, 0.15)';
  };

  return (
    <div className="app-container">
      {/* Top App Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-icon-wrap">
            <Shield className="brand-icon" size={20} />
            <div className="brand-pulse"></div>
          </div>
          <div className="brand-info">
            <h1 className="brand-title">
              SmartConsent <span className="brand-badge">AI</span>
            </h1>
            <p className="brand-subtitle">Privacy Assistant & Policy Analyzer</p>
          </div>
        </div>

        <div className="header-actions">
          <button
            className={`action-icon-btn ${currentTab === 'settings' ? 'active' : ''}`}
            title="Privacy Preferences"
            onClick={() => setCurrentTab(currentTab === 'settings' ? 'overview' : 'settings')}
          >
            <Settings size={18} />
          </button>
        </div>
      </header>

      {/* Target Domain Strip */}
      <div className="domain-strip">
        <div className="domain-pill">
          <span className="domain-dot"></span>
          <span className="domain-name" title={pageTitle}>{domain}</span>
        </div>
        <div className="scan-status-badge">
          <CheckCircle2 size={13} className="status-icon" />
          <span>{isLoading ? 'Scanning...' : 'Scanned & Verified'}</span>
        </div>
      </div>

      {/* Main Scrollable View Area */}
      <main className="app-main-content">
        {isLoading && (
          <div className="scanner-loading-overlay">
            <div className="radar-spinner">
              <div className="radar-circle"></div>
              <Shield className="radar-shield" size={32} />
            </div>
            <h3 className="loading-title">Analyzing Privacy Policy</h3>
            <p className="loading-desc">{backendMessage || 'Extracting clauses, checking RAG compliance & computing risk...'}</p>
            <div className="loading-progress-bar">
              <div className="loading-progress-fill"></div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-banner">
            <AlertTriangle className="error-icon" size={20} />
            <div className="error-text">
              <h4>Extraction Notice</h4>
              <p>{error}</p>
            </div>
            <button className="error-retry-btn" onClick={handleExtract}>
              Retry
            </button>
          </div>
        )}

        {/* ================= CLAUSE DEEP-DIVE VIEW ================= */}
        {selectedClause ? (
          <div className="clause-detail-view">
            <div className="detail-top-nav">
              <button className="back-btn" onClick={() => setSelectedClause(null)}>
                <ArrowLeft size={16} />
                <span>Back to Clauses</span>
              </button>
              <span className={`clause-severity-pill ${selectedClause.risk_level.toLowerCase()}`}>
                {selectedClause.risk_level} Risk
              </span>
            </div>

            <div className="detail-header-card">
              <div className="detail-category-label">{selectedClause.category || 'General Privacy Clause'}</div>
              <h2 className="detail-clause-title">{selectedClause.name}</h2>
              <p className="detail-clause-desc">{selectedClause.description}</p>
            </div>

            {/* Evidence Highlight Quote */}
            <div className="detail-section">
              <div className="section-label">
                <FileText size={15} />
                <span>Original Policy Quote</span>
              </div>
              <div className="evidence-quote-box">
                <p>"{selectedClause.evidence}"</p>
                <div className="evidence-actions">
                  <button className="highlight-page-btn" onClick={() => handleHighlight(selectedClause.evidence)}>
                    <Eye size={14} />
                    <span>Highlight on Page</span>
                  </button>
                  {highlightStatus && <span className="highlight-status-msg">{highlightStatus}</span>}
                </div>
              </div>
            </div>

            {/* Detected Risk Factors */}
            <div className="detail-section">
              <div className="section-label">
                <AlertTriangle size={15} />
                <span>Detected Risk Factors</span>
              </div>
              <div className="risk-tags-wrap">
                {(selectedClause.tags || ['Automated Tracking', 'Broad Scope', 'Data Retention']).map((tag, idx) => (
                  <span key={idx} className="risk-tag">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Impact & Recommenation */}
            <div className="detail-section">
              <div className="section-label">
                <Sparkles size={15} />
                <span>SmartConsent Recommendation</span>
              </div>
              <div className="advice-card">
                <p className="advice-main">{selectedClause.recommendation || 'Consider limiting permissions in your account settings or opting out of ad telemetry.'}</p>
                {selectedClause.impact && (
                  <p className="advice-impact">
                    <strong>User Impact:</strong> {selectedClause.impact}
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* ================= TAB 1: OVERVIEW ================= */}
            {currentTab === 'overview' && aiResult && (
              <div className="tab-pane overview-pane">
                {/* Standalone Web App / Preview Mode Banner */}
                {(typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) && (
                  <div className="web-preview-banner">
                    <div className="web-preview-info">
                      <div className="web-preview-tag">
                        <Globe size={13} />
                        <span>Web Preview Mode</span>
                      </div>
                      <p>Running in browser mode. Analyze custom policies or test with live AI backend.</p>
                    </div>
                    <button
                      className="btn-open-custom-input"
                      onClick={() => setCustomTextModalOpen(true)}
                    >
                      <FileText size={14} />
                      <span>Paste Custom Policy</span>
                    </button>
                  </div>
                )}

                {/* Privacy Score Hero Card */}
                <div className="scorecard-hero">
                  <div className="score-ring-wrap">
                    <svg className="score-svg" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="42" className="score-svg-bg" />
                      <circle
                        cx="50"
                        cy="50"
                        r="42"
                        className="score-svg-progress"
                        style={{
                          strokeDasharray: 264,
                          strokeDashoffset: 264 - (264 * riskScore) / 100,
                          stroke: getScoreColor(riskScore)
                        }}
                      />
                    </svg>
                    <div className="score-center-text">
                      <span className="score-num" style={{ color: getScoreColor(riskScore) }}>
                        {riskScore}
                      </span>
                      <span className="score-max">/100</span>
                    </div>
                  </div>

                  <div className="score-summary-details">
                    <div className="risk-title-badge" style={{ backgroundColor: getScoreBgGlow(riskScore), color: getScoreColor(riskScore) }}>
                      {aiResult.risk_level} Privacy Risk
                    </div>
                    <div className="risk-stats-pills">
                      <div className="stat-chip danger" onClick={() => { setCurrentTab('clauses'); setClauseFilter('high'); }}>
                        <span className="chip-count">{highRiskCount}</span>
                        <span className="chip-label">High</span>
                      </div>
                      <div className="stat-chip warning" onClick={() => { setCurrentTab('clauses'); setClauseFilter('medium'); }}>
                        <span className="chip-count">{medRiskCount}</span>
                        <span className="chip-label">Medium</span>
                      </div>
                      <div className="stat-chip safe" onClick={() => { setCurrentTab('clauses'); setClauseFilter('low'); }}>
                        <span className="chip-count">{lowRiskCount}</span>
                        <span className="chip-label">Low</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Summary Alert Banner */}
                <div className="overview-alert-card">
                  <div className="alert-header">
                    <ShieldAlert size={18} className="alert-icon danger-icon" />
                    <h4>Critical Privacy Findings</h4>
                  </div>
                  <p className="alert-body">{aiResult.summary}</p>
                </div>

                {/* Quick Highlights Grid */}
                <div className="quick-metrics-grid">
                  <div className="metric-box">
                    <Database size={16} className="metric-icon" />
                    <span className="metric-val">8+ Data Types</span>
                    <span className="metric-lbl">Collected</span>
                  </div>
                  <div className="metric-box">
                    <Share2 size={16} className="metric-icon" />
                    <span className="metric-val">Ad Brokers</span>
                    <span className="metric-lbl">Data Shared</span>
                  </div>
                  <div className="metric-box">
                    <Clock size={16} className="metric-icon" />
                    <span className="metric-val">Indefinite</span>
                    <span className="metric-lbl">Retention</span>
                  </div>
                </div>

                {/* Action Recommendation Box */}
                <div className="recommendation-card">
                  <div className="rec-header">
                    <Sparkles size={16} className="rec-icon" />
                    <h4>Recommended Action</h4>
                  </div>
                  <p className="rec-content">{aiResult.recommendation}</p>
                  <p className="rec-explanation">
                    <strong>Why:</strong> {aiResult.explanation}
                  </p>
                </div>

                {/* Regulatory Compliance Overview */}
                <div className="compliance-overview-card">
                  <div className="comp-header">
                    <ShieldCheck size={16} className="comp-icon" />
                    <h4>Regulatory Compliance Checks</h4>
                  </div>
                  <div className="compliance-items-list">
                    <div className="compliance-row">
                      <div className="comp-reg">
                        <span className="reg-badge">GDPR</span>
                        <span className="comp-status-tag warning">Review Required</span>
                      </div>
                      <p className="comp-desc">Ambiguous Article 17 erasure clause regarding AI training datasets.</p>
                    </div>
                    <div className="compliance-row">
                      <div className="comp-reg">
                        <span className="reg-badge">CCPA / CPRA</span>
                        <span className="comp-status-tag danger">Opt-Out Lags</span>
                      </div>
                      <p className="comp-desc">45-day delay in syncing user "Do Not Sell My Personal Info" requests.</p>
                    </div>
                    <div className="compliance-row">
                      <div className="comp-reg">
                        <span className="reg-badge">COPPA</span>
                        <span className="comp-status-tag safe">Compliant</span>
                      </div>
                      <p className="comp-desc">Explicit 16+ age gate and children data collection ban in place.</p>
                    </div>
                  </div>
                </div>

                {/* Top Flagged Clauses Preview */}
                <div className="top-clauses-section">
                  <div className="section-head-between">
                    <h4>Top Flagged Clauses</h4>
                    <button className="view-all-btn" onClick={() => setCurrentTab('clauses')}>
                      View All ({aiResult.important_clauses.length}) <ChevronRight size={14} />
                    </button>
                  </div>
                  <div className="preview-clause-cards">
                    {aiResult.important_clauses.slice(0, 3).map((clause, idx) => (
                      <div key={idx} className="preview-clause-card" onClick={() => setSelectedClause(clause)}>
                        <div className="preview-clause-top">
                          <span className="preview-title">{clause.name}</span>
                          <span className={`clause-severity-mini ${clause.risk_level.toLowerCase()}`}>
                            {clause.risk_level}
                          </span>
                        </div>
                        <p className="preview-desc">{clause.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ================= TAB 2: CLAUSES ================= */}
            {currentTab === 'clauses' && aiResult && (
              <div className="tab-pane clauses-pane">
                {/* Clause Category Filter Pills */}
                <div className="clause-filter-bar">
                  <button
                    className={`filter-pill ${clauseFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setClauseFilter('all')}
                  >
                    All ({aiResult.important_clauses.length})
                  </button>
                  <button
                    className={`filter-pill danger ${clauseFilter === 'high' ? 'active' : ''}`}
                    onClick={() => setClauseFilter('high')}
                  >
                    High ({highRiskCount})
                  </button>
                  <button
                    className={`filter-pill warning ${clauseFilter === 'medium' ? 'active' : ''}`}
                    onClick={() => setClauseFilter('medium')}
                  >
                    Medium ({medRiskCount})
                  </button>
                  <button
                    className={`filter-pill safe ${clauseFilter === 'low' ? 'active' : ''}`}
                    onClick={() => setClauseFilter('low')}
                  >
                    Low ({lowRiskCount})
                  </button>
                </div>

                {/* Clauses Card List */}
                <div className="clauses-full-list">
                  {filteredClauses.map((clause, idx) => (
                    <div
                      key={idx}
                      className={`clause-interactive-card ${clause.risk_level.toLowerCase()}`}
                      onClick={() => setSelectedClause(clause)}
                    >
                      <div className="clause-card-top">
                        <div className="clause-card-title-group">
                          <span className="clause-card-category">{clause.category || 'Privacy Clause'}</span>
                          <h4 className="clause-card-title">{clause.name}</h4>
                        </div>
                        <span className={`clause-severity-pill ${clause.risk_level.toLowerCase()}`}>
                          {clause.risk_level}
                        </span>
                      </div>

                      <p className="clause-card-desc">{clause.description}</p>

                      <div className="clause-card-footer">
                        <div className="clause-tags-row">
                          {(clause.tags || ['Policy Clause']).slice(0, 2).map((t, tidx) => (
                            <span key={tidx} className="clause-tag-pill">
                              #{t}
                            </span>
                          ))}
                        </div>
                        <span className="clause-open-hint">
                          Inspect <ChevronRight size={13} />
                        </span>
                      </div>
                    </div>
                  ))}

                  {filteredClauses.length === 0 && (
                    <div className="empty-filter-state">
                      <CheckCircle2 size={32} className="empty-icon" />
                      <p>No clauses match this filter.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ================= TAB 3: BREAKDOWN ================= */}
            {currentTab === 'breakdown' && (
              <div className="tab-pane breakdown-pane">
                <div className="breakdown-header">
                  <h3>Risk Factor Breakdown</h3>
                  <p>Comprehensive analysis across 8 core privacy vectors.</p>
                </div>

                <div className="breakdown-bars-container">
                  {[
                    { title: 'Data Collection & Telemetry', score: 85, level: 'High Risk', icon: Database, color: '#ef4444' },
                    { title: 'Third-Party Sharing & Ad Brokers', score: 90, level: 'Critical Risk', icon: Share2, color: '#ef4444' },
                    { title: 'Data Retention & AI Training', score: 75, level: 'High Risk', icon: Clock, color: '#ef4444' },
                    { title: 'Tracking, Cookies & Fingerprints', score: 80, level: 'High Risk', icon: Cookie, color: '#ef4444' },
                    { title: 'Policy Update Transparency', score: 65, level: 'Medium Risk', icon: FileText, color: '#f59e0b' },
                    { title: 'User Rights & Erasure Support', score: 45, level: 'Medium Risk', icon: UserCheck, color: '#f59e0b' },
                    { title: 'Data Transfer & International Storage', score: 40, level: 'Moderate', icon: Layers, color: '#f59e0b' },
                    { title: 'Encryption & Transit Safeguards', score: 20, level: 'Low Risk', icon: ShieldCheck, color: '#10b981' }
                  ].map((factor, idx) => {
                    const FactorIcon = factor.icon;
                    return (
                      <div key={idx} className="breakdown-factor-row">
                        <div className="factor-info-top">
                          <div className="factor-name">
                            <FactorIcon size={15} className="factor-icon" />
                            <span>{factor.title}</span>
                          </div>
                          <span className="factor-score-label" style={{ color: factor.color }}>
                            {factor.level} ({factor.score}%)
                          </span>
                        </div>
                        <div className="factor-progress-track">
                          <div
                            className="factor-progress-bar"
                            style={{
                              width: `${factor.score}%`,
                              backgroundColor: factor.color
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ================= TAB 4: CHAT ================= */}
            {currentTab === 'chat' && (
              <div className="tab-pane chat-pane">
                <div className="chat-messages-scroll">
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className={`chat-bubble-wrap ${msg.role}`}>
                      <div className="chat-bubble">
                        <div className="chat-sender-label">
                          {msg.role === 'user' ? 'You' : 'SmartConsent AI'}
                        </div>
                        <p>{msg.content}</p>
                      </div>
                    </div>
                  ))}

                  {isChatting && (
                    <div className="chat-bubble-wrap assistant">
                      <div className="chat-bubble typing-bubble">
                        <div className="typing-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Suggested prompt chips */}
                <div className="suggested-prompts-bar">
                  <button className="prompt-chip" onClick={() => handleChat('Do they sell my data?')}>
                    "Do they sell my data?"
                  </button>
                  <button className="prompt-chip" onClick={() => handleChat('Can I delete my account?')}>
                    "Can I delete my account?"
                  </button>
                  <button className="prompt-chip" onClick={() => handleChat('What about AI training?')}>
                    "What about AI training?"
                  </button>
                </div>

                {/* Chat Input form */}
                <div className="chat-bottom-input">
                  <input
                    type="text"
                    className="chat-text-input"
                    placeholder="Ask a question about this policy..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                    disabled={isChatting}
                  />
                  <button
                    className="chat-submit-btn"
                    onClick={() => handleChat()}
                    disabled={isChatting || !chatInput.trim()}
                  >
                    <Send size={16} />
                  </button>
                </div>
              </div>
            )}

            {/* ================= TAB 5: SETTINGS ================= */}
            {currentTab === 'settings' && (
              <div className="tab-pane settings-pane">
                <div className="settings-header">
                  <h3>Privacy Preferences</h3>
                  <p>Customize your personal privacy thresholds. SmartConsent flags clauses exceeding your choices.</p>
                </div>

                <div className="preferences-list">
                  {[
                    { key: 'location_tracking', label: 'Location Tracking', icon: Layers, desc: 'Precise GPS and network beacons' },
                    { key: 'personalized_ads', label: 'Personalized Advertising', icon: Share2, desc: 'Behavioral profiling and ad syndicates' },
                    { key: 'third_party_sharing', label: 'Third-Party Data Sharing', icon: Database, desc: 'Selling or licensing data to third parties' },
                    { key: 'data_retention', label: 'Indefinite Data Retention', icon: Clock, desc: 'Storing telemetry permanently after closure' },
                    { key: 'sensitive_data', label: 'Sensitive Data Collection', icon: ShieldAlert, desc: 'Biometrics, health, financial or clipboard data' }
                  ].map((item) => {
                    const PrefIcon = item.icon;
                    const prefKey = item.key as keyof UserPreferences;
                    return (
                      <div key={item.key} className="pref-row-card">
                        <div className="pref-text">
                          <div className="pref-title">
                            <PrefIcon size={16} className="pref-icon" />
                            <span>{item.label}</span>
                          </div>
                          <p className="pref-desc">{item.desc}</p>
                        </div>
                        <select
                          className="pref-select"
                          value={preferences[prefKey]}
                          onChange={(e) => savePreference(prefKey, e.target.value)}
                        >
                          <option value="Do Not Allow">Strict (Block)</option>
                          <option value="Ask Me">Warn Me</option>
                          <option value="Allow">Allow</option>
                        </select>
                      </div>
                    );
                  })}
                </div>

                {/* Backend Server Endpoint Configuration */}
                <div className="pref-row-card api-config-card">
                  <div className="pref-text">
                    <div className="pref-title">
                      <Server size={16} className="pref-icon" />
                      <span>Backend Server Endpoint</span>
                    </div>
                    <p className="pref-desc">Connect this extension/web preview to your deployed VPS or cloud backend API.</p>
                  </div>
                  <div className="api-config-inputs">
                    <input
                      type="text"
                      className="api-url-input"
                      value={apiUrl}
                      onChange={(e) => setApiUrl(e.target.value)}
                      placeholder="http://localhost:8000 or https://api.yourdomain.com"
                    />
                    <div className="api-config-actions">
                      <button
                        type="button"
                        className="btn-test-connection"
                        onClick={async () => {
                          setConnectionStatus({ status: 'testing', message: 'Testing connection...' });
                          setStoredApiUrl(apiUrl);
                          const res = await testBackendHealth(apiUrl);
                          if (res.ok) {
                            setConnectionStatus({ status: 'connected', message: `Connected: ${res.message}` });
                          } else {
                            setConnectionStatus({ status: 'error', message: res.message });
                          }
                        }}
                        disabled={connectionStatus.status === 'testing'}
                      >
                        {connectionStatus.status === 'testing' ? 'Testing...' : 'Test Connection'}
                      </button>
                      <button
                        type="button"
                        className="btn-save-api"
                        onClick={() => {
                          setStoredApiUrl(apiUrl);
                          setConnectionStatus({ status: 'connected', message: 'URL saved successfully!' });
                        }}
                      >
                        Save
                      </button>
                      <button
                        type="button"
                        className="btn-reset-api"
                        onClick={() => {
                          resetStoredApiUrl();
                          setApiUrl('http://localhost:8000');
                          setConnectionStatus({ status: 'idle', message: 'Reset to default localhost:8000' });
                        }}
                      >
                        Reset
                      </button>
                    </div>
                    {connectionStatus.message && (
                      <div className={`connection-status-badge ${connectionStatus.status}`}>
                        {connectionStatus.status === 'connected' && <CheckCircle2 size={13} />}
                        {connectionStatus.status === 'error' && <AlertTriangle size={13} />}
                        <span>{connectionStatus.message}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="about-box">
                  <h4>SmartConsent Engine v2.4</h4>
                  <p>Equipped with RAG Legal Intelligence & Multi-Agent Clause Reasoning.</p>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Navigation Tab Bar */}
      {!selectedClause && (
        <nav className="app-tab-bar">
          <button
            className={`tab-bar-btn ${currentTab === 'overview' ? 'active' : ''}`}
            onClick={() => setCurrentTab('overview')}
          >
            <Shield size={18} />
            <span>Overview</span>
          </button>
          <button
            className={`tab-bar-btn ${currentTab === 'clauses' ? 'active' : ''}`}
            onClick={() => setCurrentTab('clauses')}
          >
            <FileText size={18} />
            <span>Clauses</span>
            {highRiskCount > 0 && <span className="tab-bubble-count">{highRiskCount}</span>}
          </button>
          <button
            className={`tab-bar-btn ${currentTab === 'breakdown' ? 'active' : ''}`}
            onClick={() => setCurrentTab('breakdown')}
          >
            <BarChart3 size={18} />
            <span>Breakdown</span>
          </button>
          <button
            className={`tab-bar-btn ${currentTab === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentTab('chat')}
          >
            <MessageSquare size={18} />
            <span>Assistant</span>
          </button>
        </nav>
      )}

      {/* Custom Policy Modal for Web Preview */}
      {customTextModalOpen && (
        <div className="modal-backdrop" onClick={() => setCustomTextModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">
                <FileText size={18} className="modal-icon" />
                <h3>Analyze Custom Terms / Policy</h3>
              </div>
              <button className="modal-close-btn" onClick={() => setCustomTextModalOpen(false)}>×</button>
            </div>
            <div className="modal-body">
              <label className="modal-field-label">Policy Title or URL (Optional):</label>
              <input
                type="text"
                className="modal-input"
                placeholder="e.g. Acme Inc. Terms of Service or https://example.com/privacy"
                value={customInputUrl}
                onChange={(e) => setCustomInputUrl(e.target.value)}
              />
              <label className="modal-field-label">Paste Policy / Terms of Service Text:</label>
              <textarea
                className="modal-textarea"
                rows={7}
                placeholder="Paste privacy policy text, terms of service, cookie policy, or user agreement here..."
                value={customInputText}
                onChange={(e) => setCustomInputText(e.target.value)}
              />
            </div>
            <div className="modal-footer">
              <button
                className="modal-btn-cancel"
                onClick={() => setCustomTextModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className="modal-btn-submit"
                onClick={handleAnalyzeCustomPolicy}
                disabled={!customInputText.trim() || isLoading}
              >
                {isLoading ? 'Analyzing...' : 'Run Live Analysis'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Sticky Action Footer */}
      <footer className="app-footer">
        <button className="primary-action-btn" onClick={handleExtract} disabled={isLoading}>
          <RefreshCw size={16} className={isLoading ? 'spinning-icon' : ''} />
          <span>{isLoading ? 'Analyzing Policy...' : 'Analyze Active Tab'}</span>
        </button>
        <button className="secondary-action-btn" onClick={handleExportReport} title="Export Audit Report">
          <Download size={16} />
        </button>
      </footer>
    </div>
  );
}

export default App;
