const platformColors: Record<string, string> = {
  leetcode: 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400',
  codeforces: 'border-blue-500/30 bg-blue-500/10 text-blue-400',
  codechef: 'border-orange-500/30 bg-orange-500/10 text-orange-400',
  hackerrank: 'border-green-500/30 bg-green-500/10 text-green-400',
}

export default function PlatformBadge({ platform, username }: { platform: string; username: string }) {
  const colors = platformColors[platform] || 'border-white/20 bg-white/10 text-white'
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm ${colors}`}>
      <span className="font-medium capitalize">{platform}</span>
      <span className="text-xs opacity-70">{username}</span>
    </span>
  )
}
