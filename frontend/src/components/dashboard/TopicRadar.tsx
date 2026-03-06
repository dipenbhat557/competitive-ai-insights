'use client'

export default function TopicRadar({ topics }: { topics: Record<string, number> }) {
  const sorted = Object.entries(topics)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)

  if (sorted.length < 3) return null

  const max = sorted[0][1]
  const n = sorted.length
  const size = 280
  const center = size / 2
  const radius = 100

  const points = sorted.map(([, count], i) => {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2
    const r = (count / max) * radius
    return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) }
  })

  const polygon = points.map(p => `${p.x},${p.y}`).join(' ')

  return (
    <div className="card">
      <h3 className="text-base font-semibold text-white sm:text-lg">Skill Radar</h3>
      <div className="mt-2 flex items-center justify-center">
        <svg viewBox={`0 0 ${size} ${size}`} className="h-auto w-full max-w-[280px]">
          {[0.25, 0.5, 0.75, 1].map(scale => (
            <polygon
              key={scale}
              points={Array.from({ length: n }, (_, i) => {
                const angle = (Math.PI * 2 * i) / n - Math.PI / 2
                const r = scale * radius
                return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`
              }).join(' ')}
              fill="none"
              stroke="rgba(255,255,255,0.07)"
              strokeWidth="1"
            />
          ))}
          {sorted.map((_, i) => {
            const angle = (Math.PI * 2 * i) / n - Math.PI / 2
            return (
              <line
                key={i}
                x1={center} y1={center}
                x2={center + radius * Math.cos(angle)}
                y2={center + radius * Math.sin(angle)}
                stroke="rgba(255,255,255,0.05)"
                strokeWidth="1"
              />
            )
          })}
          <polygon points={polygon} fill="rgba(52,211,153,0.15)" stroke="rgb(52,211,153)" strokeWidth="2" />
          {points.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r="3" fill="rgb(52,211,153)" />
          ))}
          {sorted.map(([name], i) => {
            const angle = (Math.PI * 2 * i) / n - Math.PI / 2
            const lx = center + (radius + 24) * Math.cos(angle)
            const ly = center + (radius + 24) * Math.sin(angle)
            const display = name.length > 12 ? name.slice(0, 11) + '...' : name
            return (
              <text key={i} x={lx} y={ly} textAnchor="middle" dominantBaseline="middle" fill="#94a3b8" fontSize="10">
                {display}
              </text>
            )
          })}
        </svg>
      </div>
    </div>
  )
}
