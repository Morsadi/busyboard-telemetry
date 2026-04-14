// ─── Colours ──────────────────────────────────────────────────────────────────

export const bg = {
	base: 'bg-[#0b0f14]',
	surface: 'bg-[#0e1520]',
	surfaceDeep: 'bg-[#111820]',
	activeSession: 'bg-[#0a1f3a]',
	activeLive: 'bg-[#071a07]',
} as const;

export const border = {
	default: 'border-[#1c2a3a]',
	subtle: 'border-[#111820]',
	active: 'border-blue-600',
	live: 'border-green-800',
	lost: 'border-amber-900',
} as const;

export const text = {
	primary: 'text-[#e4eaf0]',
	muted: 'text-[#3a6080]',
	dim: 'text-[#2a4a60]',
	faint: 'text-[#1c2a3a]',
	on: 'text-green-600',
	off: 'text-[#3a6080]',
	arm: 'text-red-500',
	live: 'text-green-600',
	lost: 'text-amber-600',
	sw: 'text-blue-400',
	dev: 'text-amber-700',
	gap: 'text-amber-500', // notable gap highlight
} as const;

// ─── Typography ───────────────────────────────────────────────────────────────

export const type = {
	label: 'text-[10px] uppercase tracking-[1.5px]',
	mono: 'font-mono',
	monoSm: 'font-mono text-[11px]',
	monoXs: 'font-mono text-[10px]',
	tableCol: 'text-[9px] uppercase tracking-[1.5px] font-normal',
} as const;

// ─── Layout ───────────────────────────────────────────────────────────────────

export const layout = {
	panelHead: 'px-3 py-2.5 border-b',
	dividerY: 'border-r',
	stickyHead: 'sticky top-0 z-10',
} as const;
