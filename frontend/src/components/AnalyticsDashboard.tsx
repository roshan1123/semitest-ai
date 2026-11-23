import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getAnalyticsDevices,
  getAnalyticsFailures,
  getAnalyticsSummary,
  getAnalyticsTrends,
  type AnalyticsSummary,
  type DeviceStatistic,
  type FailurePoint,
  type TrendPoint,
} from '../services/analytics'

export function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [trends, setTrends] = useState<TrendPoint[]>([])
  const [failures, setFailures] = useState<FailurePoint[]>([])
  const [devices, setDevices] = useState<DeviceStatistic[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      getAnalyticsSummary(),
      getAnalyticsTrends(),
      getAnalyticsFailures(),
      getAnalyticsDevices(),
    ])
      .then(([summaryResult, trendResult, failureResult, deviceResult]) => {
        setSummary(summaryResult)
        setTrends(trendResult)
        setFailures(failureResult)
        setDevices(deviceResult)
      })
      .catch(() => setError('Unable to load analytics.'))
  }, [])

  const statusData = summary
    ? [
        { name: 'PASS', value: summary.pass_count, color: '#34d399' },
        { name: 'FAIL', value: summary.fail_count, color: '#f87171' },
        { name: 'REVIEW', value: summary.review_count, color: '#fbbf24' },
      ]
    : []

  return (
    <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="mb-4">
        <p className="text-sm text-slate-400">Phase 5</p>
        <h2 className="text-xl font-semibold">Analytics Dashboard</h2>
      </div>

      {error && (
        <p role="alert" className="mb-4 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-red-200">
          {error}
        </p>
      )}

      {summary && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Kpi label="Registered devices" value={summary.total_registered_devices} />
          <Kpi label="Test executions" value={summary.total_test_executions} />
          <Kpi label="PASS" value={summary.pass_count} />
          <Kpi label="FAIL" value={summary.fail_count} />
          <Kpi label="Pass percentage" value={`${summary.pass_percentage}%`} />
        </div>
      )}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <ChartCard title="Test activity over time">
          {trends.length === 0 ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={trends}>
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis allowDecimals={false} stroke="#94a3b8" />
                <Tooltip />
                <Legend />
                <Bar dataKey="PASS" stackId="status" fill="#34d399" />
                <Bar dataKey="FAIL" stackId="status" fill="#f87171" />
                <Bar dataKey="REVIEW" stackId="status" fill="#fbbf24" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="PASS / FAIL / REVIEW distribution">
          {summary && summary.total_test_executions === 0 ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90}>
                  {statusData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="Failure frequency by measurement">
          {failures.length === 0 ? (
            <EmptyChart />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={failures} layout="vertical">
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} stroke="#94a3b8" />
                <YAxis type="category" dataKey="parameter_name" width={110} stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="failure_count" fill="#f87171" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="Device-wise test summary">
          {devices.length === 0 ? (
            <EmptyChart />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="py-2">Device</th>
                    <th className="py-2">Category</th>
                    <th className="py-2">PASS</th>
                    <th className="py-2">FAIL</th>
                    <th className="py-2">Review</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.map((device) => (
                    <tr key={device.device_part_number} className="border-b border-slate-800">
                      <td className="py-2">{device.device_part_number}</td>
                      <td className="py-2">{device.device_category}</td>
                      <td className="py-2 text-emerald-300">{device.PASS}</td>
                      <td className="py-2 text-red-300">{device.FAIL}</td>
                      <td className="py-2 text-amber-300">{device.REVIEW}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </ChartCard>
      </div>
    </section>
  )
}

function Kpi({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-slate-800 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  )
}

function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-800 p-4">
      <h3 className="mb-3 font-semibold">{title}</h3>
      {children}
    </div>
  )
}

function EmptyChart() {
  return <p className="py-20 text-center text-sm text-slate-400">No simulation data available yet.</p>
}
