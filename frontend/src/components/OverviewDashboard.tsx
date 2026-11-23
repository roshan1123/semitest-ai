import { useEffect, useState } from 'react'

import {
  getAnalyticsSummary,
  type AnalyticsSummary,
} from '../services/analytics'
import { listTests } from '../services/tests'
import type { TestExecution } from '../types/testExecution'

type OverviewTarget = 'Devices' | 'Profiles' | 'Testing' | 'Analytics' | 'Inspection'

type OverviewDashboardProps = {
  onNavigate: (target: OverviewTarget) => void
}

export function OverviewDashboard({ onNavigate }: OverviewDashboardProps) {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [recentTests, setRecentTests] = useState<TestExecution[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getAnalyticsSummary(), listTests()])
      .then(([summaryResult, tests]) => {
        setSummary(summaryResult)
        setRecentTests(tests.slice(0, 5))
      })
      .catch(() => setError('Unable to load overview data.'))
  }, [])

  return (
    <section className="space-y-5">
      <div>
        <p className="text-sm text-slate-400">Executive workspace</p>
        <h2 className="text-2xl font-semibold">Simulation Overview</h2>
        <p className="mt-1 text-sm text-slate-400">
          A concise view of test activity and recommended next actions.
        </p>
      </div>

      {error && (
        <p role="alert" className="rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-red-200">
          {error}
        </p>
      )}

      {summary && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <OverviewKpi label="Registered devices" value={summary.total_registered_devices} />
          <OverviewKpi label="Test executions" value={summary.total_test_executions} />
          <OverviewKpi label="Pass percentage" value={`${summary.pass_percentage}%`} />
          <OverviewKpi
            label="Needs attention"
            value={summary.fail_count + summary.review_count}
            accent="text-amber-300"
          />
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold">Recent test activity</h3>
            <button
              type="button"
              onClick={() => onNavigate('Testing')}
              className="text-sm font-semibold text-cyan-300 hover:text-cyan-200"
            >
              View testing
            </button>
          </div>

          {recentTests.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-700 py-10 text-center text-sm text-slate-400">
              No recent simulated tests.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="py-2">Device</th>
                    <th className="py-2">Scenario</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTests.map((test) => (
                    <tr key={test.id} className="border-b border-slate-800">
                      <td className="py-2">{test.device_part_number}</td>
                      <td className="py-2">{test.scenario}</td>
                      <td className={testStatusClass(test.overall_status)}>{test.overall_status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <aside className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
          <h3 className="font-semibold">Quick actions</h3>
          <div className="mt-4 space-y-2">
            <QuickAction label="Register a device" onClick={() => onNavigate('Devices')} />
            <QuickAction label="Configure test profile" onClick={() => onNavigate('Profiles')} />
            <QuickAction label="Start simulated test" onClick={() => onNavigate('Testing')} />
            <QuickAction label="Inspect an image" onClick={() => onNavigate('Inspection')} />
            <QuickAction label="Open detailed analytics" onClick={() => onNavigate('Analytics')} />
          </div>
        </aside>
      </div>
    </section>
  )
}

function OverviewKpi({
  label,
  value,
  accent = 'text-slate-100',
}: {
  label: string
  value: number | string
  accent?: string
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-1 text-3xl font-semibold ${accent}`}>{value}</p>
    </div>
  )
}

function QuickAction({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-lg border border-slate-700 px-3 py-2 text-left text-sm text-slate-200 hover:border-cyan-400/60 hover:bg-cyan-400/5"
    >
      {label}
    </button>
  )
}

function testStatusClass(status: 'PASS' | 'FAIL' | 'REVIEW') {
  if (status === 'PASS') return 'font-semibold text-emerald-300'
  if (status === 'FAIL') return 'font-semibold text-red-300'
  return 'font-semibold text-amber-300'
}
