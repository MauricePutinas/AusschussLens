import { useEffect, useState } from 'react'
import Layout from './components/Layout'
import ErfassenView from './views/ErfassenView'
import HistorieView from './views/HistorieView'
import AnalyseView from './views/AnalyseView'
import ReportView from './views/ReportView'
import { api, ScrapEvent } from './api'

export default function App() {
  const [tab, setTab] = useState('erfassen')
  const [provider, setProvider] = useState('mock')
  const [selected, setSelected] = useState<ScrapEvent | null>(null)
  const [version, setVersion] = useState(0)
  const reload = () => setVersion((v) => v + 1)

  useEffect(() => {
    api.health().then((h) => setProvider(h.llm_provider || 'mock')).catch(() => {})
  }, [])

  const openReport = (e: ScrapEvent) => { setSelected(e); setTab('report') }

  return (
    <Layout active={tab === 'report' ? 'historie' : tab} setTab={setTab} provider={provider}>
      {tab === 'erfassen' && <ErfassenView onCreated={(e) => { reload(); openReport(e) }} />}
      {tab === 'historie' && <HistorieView version={version} onOpen={openReport} onChange={reload} />}
      {tab === 'analyse' && <AnalyseView version={version} />}
      {tab === 'report' && selected && (
        <ReportView event={selected} provider={provider} onBack={() => setTab('historie')} onChange={reload} />
      )}
    </Layout>
  )
}
