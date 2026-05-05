import { useState, useEffect, useMemo, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './index.css'

function App() {
  const [activeTab, setActiveTab] = useState('manage')
  const [loading, setLoading] = useState(false)
  
  // Toast State
  const [toasts, setToasts] = useState([])
  const showToast = (message, type = 'success') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000)
  }

  // WebSocket / Progress State
  const [wsProgress, setWsProgress] = useState(null)
  const ws = useRef(null)

  useEffect(() => {
    const connectWS = () => {
      ws.current = new WebSocket('ws://127.0.0.1:8000/ws')
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'progress') {
          setWsProgress({ message: data.message, percent: data.percent })
        } else if (data.type === 'finished' || data.type === 'error') {
          if (data.type === 'error') showToast(data.message, 'error')
          else showToast('知识库更新完成')
          setWsProgress(null)
          fetchDocuments() // Refresh list on finish
        }
      }
      ws.current.onclose = () => setTimeout(connectWS, 3000)
    }
    connectWS()
    return () => ws.current?.close()
  }, [])

  // Query State
  const [queryForm, setQueryForm] = useState({ company_name: '', question: '' })
  const [queryResult, setQueryResult] = useState(null)
  const [queryError, setQueryError] = useState(null)

  // Document Management State
  const [ingestForm, setIngestForm] = useState({ company_name: '', file: null })
  const [documents, setDocuments] = useState([])
  const [fetchingDocs, setFetchingDocs] = useState(false)
  
  // Search & Pagination State
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 8

  const API_BASE_URL = 'http://127.0.0.1:8000'

  const fetchDocuments = async () => {
    setFetchingDocs(true)
    try {
      const res = await fetch(`${API_BASE_URL}/documents`)
      if (res.ok) {
        const data = await res.json()
        setDocuments(data)
      }
    } catch (err) {
      showToast('获取数据失败', 'error')
    } finally {
      setFetchingDocs(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  // Filtered & Paginated Documents
  const filteredDocs = useMemo(() => {
    return documents.filter(doc => 
      doc.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.sha1.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [documents, searchTerm])

  const paginatedDocs = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return filteredDocs.slice(start, start + pageSize)
  }, [filteredDocs, currentPage])

  const totalPages = Math.ceil(filteredDocs.length / pageSize) || 1

  const handleQuerySubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setQueryResult(null)
    setQueryError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: queryForm.company_name, question: queryForm.question, schema_type: "number" })
      })
      if (!response.ok) throw new Error((await response.json()).detail || '分析失败')
      setQueryResult(await response.json())
      showToast('分析结果已就绪')
    } catch (err) {
      setQueryError(err.message)
      showToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleIngestSubmit = async (e) => {
    e.preventDefault()
    if (!ingestForm.file) return
    setLoading(true)
    const formData = new FormData()
    formData.append('company_name', ingestForm.company_name)
    // removed currency and major_industry
    formData.append('file', ingestForm.file)
    try {
      const res = await fetch(`${API_BASE_URL}/ingest`, { method: 'POST', body: formData })
      if (!res.ok) throw new Error('上传失败')
      showToast('知识入库指令已发出')
      setIngestForm({ company_name: '', file: null })
      e.target.reset()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDocument = async (sha1) => {
    if (!window.confirm("确定删除吗？这会清理所有的索引数据。")) return
    try {
      const res = await fetch(`${API_BASE_URL}/documents/${sha1}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('删除失败')
      showToast('文档已移除')
      fetchDocuments()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  return (
    <>
      <header className="top-header">
        <div className="header-left">
          <div className="header-logo">
            <span style={{fontSize: '1.2rem'}}>🏢</span> 企业知识库
          </div>
          <div className="header-breadcrumb">
            / {activeTab === 'query' ? '问答统计' : '文档管理'}
          </div>
        </div>
        <div className="header-right">
          <span>管理员</span>
          <div className="avatar">管</div>
        </div>
      </header>

      <div className="layout">
        {/* Toast System */}
        <div className="toast-container">
          {toasts.map(t => (
            <div key={t.id} className={`toast ${t.type}`}>
              <span style={{fontSize: '1.2rem'}}>{t.type === 'success' ? '✅' : '❌'}</span>
              {t.message}
            </div>
          ))}
        </div>

        {/* Progress HUD */}
        {wsProgress && (
          <div className="progress-hud">
            <div style={{fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)'}}>系统处理中</div>
            <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>{wsProgress.message}</div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{width: `${wsProgress.percent}%`}}></div>
            </div>
            <div style={{fontSize: '0.8rem', textAlign: 'right'}}>{wsProgress.percent}%</div>
          </div>
        )}

        <aside className="sidebar">
          <div className="nav-group">
            <div className="nav-group-title">对话</div>
            <button className="nav-item">💬 对话管理</button>
            <button className={`nav-item ${activeTab === 'query' ? 'active' : ''}`} onClick={() => setActiveTab('query')}>
              📊 问答统计
            </button>
          </div>
          
          <div className="nav-group">
            <div className="nav-group-title">知识库</div>
            <button className={`nav-item ${activeTab === 'manage' ? 'active' : ''}`} onClick={() => setActiveTab('manage')}>
              📚 文档管理
            </button>
            <button className="nav-item">🔍 检索测试</button>
          </div>
          
          <div className="nav-group">
            <div className="nav-group-title">系统设置</div>
            <button className="nav-item">⚙️ 权限配置</button>
            <button className="nav-item">👤 身份映射</button>
            <button className="nav-item">📝 审计日志</button>
            <button className="nav-item">🛠 系统配置</button>
          </div>
        </aside>

        <main className="main-wrapper">
          {activeTab === 'query' && (
            <>
              {/* Dummy stats for BI look */}
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#1677ff'}}>8,432</div>
                  <div className="stat-label">总问答次数</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#52c41a'}}>87%</div>
                  <div className="stat-label">用户满意度</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#1677ff'}}>0.92</div>
                  <div className="stat-label">平均检索得分</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#1677ff'}}>1.1s</div>
                  <div className="stat-label">平均响应时间</div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">发起 AI 测试对话</div>
                <form onSubmit={handleQuerySubmit}>
                  <div className="form-group">
                    <label>知识域 (公司名)</label>
                    <input type="text" required placeholder="例如: Holley Inc." value={queryForm.company_name} onChange={e => setQueryForm({...queryForm, company_name: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>测试问题</label>
                    <input type="text" required placeholder="请输入..." value={queryForm.question} onChange={e => setQueryForm({...queryForm, question: e.target.value})} />
                  </div>
                  <button type="submit" className="btn" disabled={loading}>
                    {loading ? '分析中...' : '提交测试'}
                  </button>
                </form>

                {queryError && <div style={{color: 'red', marginTop: '16px'}}>{queryError}</div>}

                {queryResult && (
                  <div className="result-box">
                    <div style={{fontWeight: 600, marginBottom: '12px'}}>分析结论</div>
                    <div className="result-content">
                      <ReactMarkdown>{queryResult.value}</ReactMarkdown>
                    </div>
                    {queryResult.references && (
                      <div style={{marginTop: '16px'}}>
                        <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>参考来源:</div>
                        <div className="chips-container">
                          {queryResult.references.map((ref, idx) => (
                            <span key={idx} className="chip">📄 第 {ref.page_index + 1} 页 ({ref.pdf_sha1.substring(0,6)})</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'manage' && (
            <>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#2b6de1'}}>{documents.length}</div>
                  <div className="stat-label">知识文档总数</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#2b6de1'}}>{new Set(documents.map(d=>d.company_name)).size}</div>
                  <div className="stat-label">涵盖知识域 (公司)</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{color: '#52c41a'}}>{wsProgress ? '入库中' : '正常'}</div>
                  <div className="stat-label">索引引擎状态</div>
                </div>
              </div>

              <div className="card">
                <div className="card-header" style={{borderBottom: '1px solid #f0f0f0', paddingBottom: '16px', marginBottom: '16px'}}>导入新知识</div>
                <form onSubmit={handleIngestSubmit} style={{display: 'flex', gap: '16px', alignItems: 'flex-end'}}>
                  <div className="form-group" style={{flex: 1, marginBottom: 0}}>
                    <label>归属知识域 (公司名)</label>
                    <input type="text" required placeholder="输入名称..." value={ingestForm.company_name} onChange={e => setIngestForm({...ingestForm, company_name: e.target.value})} />
                  </div>
                  <div className="form-group" style={{flex: 2, marginBottom: 0}}>
                    <label>源文件 (PDF)</label>
                    <input type="file" accept=".pdf" required onChange={e => setIngestForm({...ingestForm, file: e.target.files[0]})} style={{border: 'none', padding: '8px 0'}}/>
                  </div>
                  <button type="submit" className="btn" disabled={loading || !!wsProgress} style={{width: '120px'}}>
                    上传并解析
                  </button>
                </form>
              </div>

              <div className="card">
                <div className="search-container">
                  <div className="card-header" style={{margin: 0}}>知识清单</div>
                  <input 
                    type="text" 
                    className="search-input" 
                    placeholder="按公司或文档 Hash 检索..." 
                    value={searchTerm} 
                    onChange={e => {setSearchTerm(e.target.value); setCurrentPage(1);}}
                  />
                </div>

                {fetchingDocs ? (
                  <div style={{padding: '20px 0'}}>
                    <div className="skeleton"></div>
                    <div className="skeleton"></div>
                    <div className="skeleton"></div>
                  </div>
                ) : (
                  <>
                    <table className="doc-table">
                      <thead>
                        <tr>
                          <th>知识域 (公司)</th>
                          <th>文档指纹 (Hash)</th>
                          <th>文件大小</th>
                          <th>解析页数</th>
                          <th style={{textAlign: 'right'}}>操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedDocs.map((doc, idx) => (
                          <tr key={idx}>
                            <td style={{fontWeight: '500'}}>{doc.company_name}</td>
                            <td style={{fontFamily: 'monospace'}}>{doc.sha1?.substring(0, 8)}...</td>
                            <td>{doc.size || '-'}</td>
                            <td>{doc.page_count !== '-' ? `${doc.page_count} 页` : '-'}</td>
                            <td style={{textAlign: 'right'}}>
                              <a href={`${API_BASE_URL}/documents/${doc.sha1}/pdf`} target="_blank" rel="noreferrer" className="btn-link">预览原件</a>
                              <span style={{color: '#f0f0f0'}}>|</span>
                              <button className="btn-danger" onClick={() => handleDeleteDocument(doc.sha1)}>删除</button>
                            </td>
                          </tr>
                        ))}
                        {paginatedDocs.length === 0 && (
                          <tr><td colSpan="5" style={{textAlign: 'center', padding: '32px', color: '#bfbfbf'}}>暂无数据</td></tr>
                        )}
                      </tbody>
                    </table>
                    
                    <div className="pagination">
                      <button className="page-btn" disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)}>上一页</button>
                      <span>{currentPage} / {totalPages}</span>
                      <button className="page-btn" disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => p + 1)}>下一页</button>
                    </div>
                  </>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </>
  )
}

export default App
