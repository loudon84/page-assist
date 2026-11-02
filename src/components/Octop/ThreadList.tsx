import { useEffect, useState } from "react"
import { Button } from "antd"
import { useNavigate } from "react-router-dom"
import { octopApi } from "@/services/octop-api"
import type { RemoteThread } from "@/services/octop-api/types"
import { listRecent } from "@/db/octop"
import { StateBanner } from "./StateBanner"

export const ThreadList = ({ expertKey }: { expertKey: string }) => {
  const [items, setItems] = useState<RemoteThread[]>([])
  const [cursor, setCursor] = useState<string | null>(null)
  const [recent, setRecent] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const load = async (next?: string, append = false) => {
    setLoading(true)
    setError(null)
    try {
      const page = await octopApi.listThreads(expertKey, next)
      setItems((prev) => (append ? [...prev, ...page.items] : page.items))
      setCursor(page.next_cursor || null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "thread list failed")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    void listRecent("").then((rows) => {
      setRecent(rows.filter((row) => row.expertKey === expertKey).map((row) => row.threadId || ""))
    })
  }, [expertKey])

  return (
    <div className="p-4 space-y-4 max-w-3xl mx-auto">
      <div className="flex items-center gap-2">
        <Button onClick={() => navigate("/enterprise/experts")}>Back</Button>
        <div className="text-sm text-gray-500">Threads</div>
      </div>
      {error ? <StateBanner marker="error" message={error} /> : null}
      {!loading && items.length === 0 ? (
        <StateBanner marker="empty" message="No threads yet." />
      ) : null}
      {recent.filter(Boolean).length ? (
        <div className="text-xs text-gray-400">Recent: {recent.filter(Boolean).join(", ")}</div>
      ) : null}
      <div className="grid gap-3">
        {items.map((thread) => (
          <button
            key={thread.thread_id}
            className="text-left rounded-xl border border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-[#1a1a1a]"
            onClick={() =>
              navigate(
                `/enterprise/experts/${encodeURIComponent(expertKey)}/threads/${encodeURIComponent(thread.thread_id)}`
              )
            }>
            <div className="font-medium">{thread.title || thread.thread_id}</div>
            <div className="text-xs text-gray-400">{thread.updated_at}</div>
          </button>
        ))}
      </div>
      {cursor ? (
        <Button onClick={() => void load(cursor, true)} disabled={loading}>
          Load more
        </Button>
      ) : null}
    </div>
  )
}
