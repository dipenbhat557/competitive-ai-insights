interface Props {
  strengths: Array<{ topic: string; score: number }>
}

export default function StrengthRadar({ strengths }: Props) {
  if (!strengths || strengths.length === 0) return null

  const size = 300
  const center = size / 2
  const radius = 120
  const n = strengths.length

  const points = strengths.map((s, i) => {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2
    const r = (s.score / 100) * radius
    return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) }
  })

  const polygon = points.map(p => `${p.x},${p.y}`).join(' ')

  return (
    <div className="card flex items-center justify-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {[0.25, 0.5, 0.75, 1].map(scale => (
          <polygon
            key={scale}
            points={Array.from({ length: n }, (_, i) => {
              const angle = (Math.PI * 2 * i) / n - Math.PI / 2
              const r = scale * radius
              return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`
            }).join(' ')}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="1"
          />
        ))}
        <polygon points={polygon} fill="rgba(52,211,153,0.2)" stroke="rgb(52,211,153)" strokeWidth="2" />
        {strengths.map((s, i) => {
          const angle = (Math.PI * 2 * i) / n - Math.PI / 2
          const lx = center + (radius + 20) * Math.cos(angle)
          const ly = center + (radius + 20) * Math.sin(angle)
          return (
            <text key={i} x={lx} y={ly} textAnchor="middle" dominantBaseline="middle" fill="#94a3b8" fontSize="11">
              {s.topic}
            </text>
          )
        })}
      </svg>
    </div>
  )
}
