export default function StatCard({ label, value, subtext }: { label: string; value: string; subtext: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-3 sm:p-4">
      <p className="text-xs text-slate-400 sm:text-sm">{label}</p>
      <p className="mt-1 text-xl font-semibold text-white sm:mt-2 sm:text-2xl">{value}</p>
      <p className="truncate text-[10px] text-slate-500 sm:text-xs">{subtext}</p>
    </div>
  )
}
