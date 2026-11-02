import { useEffect, useState } from "react"
import { Button, Input, Select } from "antd"
import { useNavigate } from "react-router-dom"
import { octopApi } from "@/services/octop-api"
import type { CatalogSource, Expert } from "@/services/octop-api/types"
import { StateBanner } from "./StateBanner"

export const ExpertCatalog = () => {
  const [items, setItems] = useState<Expert[]>([])
  const [q, setQ] = useState("")
  const [source, setSource] = useState<CatalogSource>("all")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [cursor, setCursor] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = async (cursor?: string, append = false) => {
    setLoading(true)
    setError(null)
    try {
      const page = await octopApi.listExperts({ q: q || undefined, source, cursor })
      setItems((prev) => (append ? [...prev, ...page.items] : page.items))
      setCursor(page.next_cursor || null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "catalog failed")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [source])

  return (
    <div className="p-4 space-y-4 max-w-3xl mx-auto">
      <div className="flex gap-2 flex-wrap">
        <Input
          value={q}
          placeholder="Search experts"
          onChange={(e) => setQ(e.target.value)}
          onPressEnter={() => void load()}
          className="flex-1 min-w-[160px]"
        />
        <Select
          value={source}
          className="w-36"
          onChange={(value: CatalogSource) => setSource(value)}
          options={[
            { value: "all", label: "All" },
            { value: "local", label: "Local" },
            { value: "remote", label: "Remote" }
          ]}
        />
        <Button onClick={() => void load()}>Search</Button>
      </div>
      {error ? <StateBanner marker="error" message={error} /> : null}
      {!loading && items.length === 0 ? (
        <StateBanner marker="empty" message="No experts available." />
      ) : null}
      <div className="grid gap-3">
        {items.map((expert) => {
          const disabled =
            expert.availability !== "available" || !expert.capabilities.create_thread
          return (
            <div
              key={expert.expertKey}
              className="rounded-xl border border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-[#1a1a1a]">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-lg">
                    {expert.avatar.kind === "emoji" ? expert.avatar.value : ""} {expert.name}
                  </div>
                  <div className="text-sm text-gray-500">{expert.description}</div>
                  <div className="text-xs mt-1 text-gray-400">{expert.source.label}</div>
                  {expert.unavailable_reason ? (
                    <div className="text-xs text-amber-600 mt-1">{expert.unavailable_reason}</div>
                  ) : null}
                </div>
                <div className="flex flex-col gap-2">
                  <Button
                    type="primary"
                    disabled={disabled}
                    onClick={() => navigate(`/enterprise/experts/${encodeURIComponent(expert.expertKey)}`)}>
                    Open
                  </Button>
                  <Button
                    disabled={disabled}
                    onClick={() =>
                      navigate(`/enterprise/experts/${encodeURIComponent(expert.expertKey)}?view=threads`)
                    }>
                    Threads
                  </Button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
      {cursor ? (
        <Button onClick={() => void load(cursor, true)} disabled={loading}>
          Load more
        </Button>
      ) : null}
    </div>
  )
}
