import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [leads, setLeads] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('leads');
  const [stats, setStats] = useState({ total: 0, high: 0, medium: 0, low: 0 });
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchLeads();
    fetchLogs();
  }, []);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/leads`);
      if (response.data.success) {
        setLeads(response.data.leads);
        calculateStats(response.data.leads);
      }
    } catch (error) {
      console.error('Error fetching leads:', error);
      showMessage('error', 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get(`${API}/logs?limit=50`);
      if (response.data.success) {
        setLogs(response.data.logs.reverse());
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const calculateStats = (leadsData) => {
    const stats = {
      total: leadsData.length,
      high: leadsData.filter(l => l.priority === 'HIGH').length,
      medium: leadsData.filter(l => l.priority === 'MEDIUM').length,
      low: leadsData.filter(l => l.priority === 'LOW').length,
    };
    setStats(stats);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post(`${API}/leads/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (response.data.success) {
        showMessage('success', 'CSV uploaded successfully!');
        await fetchLeads();
        await fetchLogs();
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to upload CSV');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessLeads = async () => {
    setProcessing(true);
    try {
      const response = await axios.post(`${API}/leads/process`);
      const data = response.data;
      showMessage('success', 
        `Processed ${data.total_leads} leads. ` +
        `${data.high_priority_count} high-priority, ${data.emails_sent} emails sent.`
      );
      await fetchLeads();
      await fetchLogs();
    } catch (error) {
      console.error('Error processing leads:', error);
      showMessage('error', 'Failed to process leads');
    } finally {
      setProcessing(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return 'bg-red-100 text-red-800';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
      case 'LOW': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-red-600 font-bold';
    if (score >= 40) return 'text-yellow-600 font-semibold';
    return 'text-green-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-4xl">🤖</div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">EasyFinder AI</h1>
                <p className="text-sm text-gray-600">Enterprise Lead Management System</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <label className="cursor-pointer bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center space-x-2">
                <span>📤</span>
                <span>Upload CSV</span>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={loading}
                />
              </label>
              <button
                onClick={handleProcessLeads}
                disabled={processing || leads.length === 0}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                data-testid="process-leads-button"
              >
                <span>⚡</span>
                <span>{processing ? 'Processing...' : 'Process Leads'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Message Alert */}
      {message.text && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className={`p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message.text}
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Total Leads</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-red-50 rounded-lg shadow p-6">
            <div className="text-sm text-red-600">High Priority</div>
            <div className="text-3xl font-bold text-red-700">{stats.high}</div>
          </div>
          <div className="bg-yellow-50 rounded-lg shadow p-6">
            <div className="text-sm text-yellow-600">Medium Priority</div>
            <div className="text-3xl font-bold text-yellow-700">{stats.medium}</div>
          </div>
          <div className="bg-green-50 rounded-lg shadow p-6">
            <div className="text-sm text-green-600">Low Priority</div>
            <div className="text-3xl font-bold text-green-700">{stats.low}</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('leads')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'leads'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              data-testid="leads-tab"
            >
              📊 Leads ({stats.total})
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'logs'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              data-testid="logs-tab"
            >
              📝 Activity Logs ({logs.length})
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'leads' && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            {loading ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">⏳</div>
                <div className="text-gray-600">Loading leads...</div>
              </div>
            ) : leads.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">📭</div>
                <div className="text-gray-600">No leads found. Upload a CSV file to get started.</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Industry</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Budget</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leads.map((lead, index) => (
                      <tr key={index} className="hover:bg-gray-50" data-testid={`lead-row-${index}`}>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm ${getScoreColor(lead.score)}`}>
                          <div className="font-mono text-lg">{lead.score}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(lead.priority)}`}>
                            {lead.priority}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{lead.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{lead.company}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{lead.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{lead.industry}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{lead.company_size}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${lead.budget}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="bg-white rounded-lg shadow">
            {logs.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">📋</div>
                <div className="text-gray-600">No activity logs yet. Process some leads to see logs.</div>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {logs.map((log, index) => (
                  <div key={index} className="p-4 hover:bg-gray-50" data-testid={`log-entry-${index}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${
                            log.event === 'EMAIL_SENT' ? 'bg-green-100 text-green-800' :
                            log.event === 'LEAD_SCORED' ? 'bg-blue-100 text-blue-800' :
                            log.event === 'CSV_UPLOADED' ? 'bg-purple-100 text-purple-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {log.event}
                          </span>
                          <span className="text-sm text-gray-500">
                            {new Date(log.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-700">
                          {log.event === 'LEAD_SCORED' && (
                            <span>
                              <strong>{log.data.name}</strong> ({log.data.company}) - 
                              Score: <strong>{log.data.score}</strong> | 
                              Priority: <strong>{log.data.priority}</strong>
                            </span>
                          )}
                          {log.event === 'EMAIL_SENT' && (
                            <span>
                              Email sent to <strong>{log.data.to}</strong>
                              {log.data.subject && ` - ${log.data.subject}`}
                            </span>
                          )}
                          {log.event === 'CSV_UPLOADED' && (
                            <span>
                              CSV file uploaded: <strong>{log.data.filename}</strong>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-600 text-sm">
        <p>© 2025 EasyFinder AI - Enterprise Lead Management System</p>
        <p className="mt-1">Built with FastAPI + React + MongoDB</p>
      </footer>
    </div>
  );
}

export default App;
