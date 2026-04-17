import { formatTimestamp, formatRelative, calcGap } from '@/lib/utils';
import { bg, border, text, type as t, layout } from '@/lib/styles';
import type { AuditRow, Session } from '@/types';

const PIP: Record<string, string> = {
	switch: '#185fa5',
	device: '#854f0b',
};

const VALUE_CLASS: Record<string, string> = {
	ON: text.on,
	OFF: text.off,
	ARM: text.arm,
	session_started: text.on,
	session_ended: text.off,
	connection_lost: text.lost,
};

const HEADERS = ['Timestamp', '+Rel', '', 'Source', 'Event', 'Value', 'Gap'];

type Props = { rows: AuditRow[]; session: Session };

export function EventTable({ rows, session }: Props) {
	if (rows.length === 0) {
		return <div className={`flex flex-1 items-center justify-center text-[12px] ${text.dim}`}>No events recorded.</div>;
	}

	return (
		<div className='min-h-full max-h-full flex-1 pb-4'>
			<table className='w-full border-collapse text-left'>
				<thead>
					<tr className={`${layout.stickyHead} ${bg.base}`}>
						{HEADERS.map((h) => (
							<th
								key={h}
								className={`border-b ${border.default} px-2.5 py-1.5 ${t.tableCol} ${text.dim}`}>
								{h}
							</th>
						))}
					</tr>
				</thead>
				<tbody>
					{rows.map((row, i) => {
						const nextRow = rows[i + 1];
						const gap = nextRow ? calcGap(row.event_ts, nextRow.event_ts) : null;

						return (
							<tr
								key={`${row.source_type}-${row.id}`}
								className={`border-b ${border.subtle} hover:${bg.surface}`}>
								<td className={`px-2.5 py-1.5 ${t.monoSm} ${text.muted}`}>{formatTimestamp(row.event_ts, 'table')}</td>
								<td className={`px-2.5 py-1.5 ${t.monoSm} ${text.faint}`}>{formatRelative(row.event_ts, session.started_at)}</td>
								<td className='px-2.5 py-1.5'>
									<span
										className='inline-block h-1.5 w-1.5 rounded-full'
										style={{ background: PIP[row.source_type] ?? '#3a6080' }}
									/>
								</td>
								<td className={`px-2.5 py-1.5 ${t.monoSm} ${row.source_type === 'switch' ? text.sw : text.dev}`}>
									{row.source_type === 'switch' ? row.source : row.source.slice(0, 6)}
								</td>
								<td className={`px-2.5 py-1.5 text-[11px] ${text.primary}`}>{row.event_type.replace(/_/g, ' ')}</td>
								<td className={`px-2.5 py-1.5 ${t.monoSm} ${VALUE_CLASS[row.value] ?? text.off}`}>{row.value}</td>
								<td className={`px-2.5 py-1.5 ${t.monoSm} ${gap?.notable ? text.gap : text.dim}`}>{gap?.display ?? '—'}</td>
							</tr>
						);
					})}
				</tbody>
			</table>
		</div>
	);
}
