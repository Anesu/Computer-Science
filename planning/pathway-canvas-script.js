// Pathway canvas: click a course to highlight its prerequisite ancestry and
// everything it unlocks; click empty canvas to reset.
//
// Reads the graph from the live arrow bindings, so it keeps working after the
// canvas is regenerated from curriculum/pathway.yaml.

const DIM_BOX = 0.15
const DIM_ARROW = 0.05
const BASE_ARROW = 0.6

export default function ({ editor, signal }) {
	function courseShapes() {
		return editor
			.getCurrentPageShapes()
			.filter((s) => s.type === 'geo' && !s.id.startsWith('shape:legend-'))
	}

	function graph() {
		// arrow id -> { from: prereq shape id, to: dependent shape id }
		const edges = new Map()
		for (const s of editor.getCurrentPageShapes()) {
			if (s.type !== 'arrow') continue
			const e = {}
			for (const b of editor.getBindingsFromShape(s, 'arrow')) {
				if (b.props.terminal === 'start') e.from = b.toId
				if (b.props.terminal === 'end') e.to = b.toId
			}
			if (e.from && e.to) edges.set(s.id, e)
		}
		return edges
	}

	function closure(start, edges, dir) {
		const seen = new Set([start])
		const queue = [start]
		while (queue.length) {
			const cur = queue.pop()
			for (const { from, to } of edges.values()) {
				const [a, b] = dir === 'up' ? [to, from] : [from, to]
				if (a === cur && !seen.has(b)) {
					seen.add(b)
					queue.push(b)
				}
			}
		}
		return seen
	}

	// Shapes are generated locked (read-only diagram) — ignoreShapeLock lets
	// the script still restyle them.
	function setOpacities(updates) {
		editor.run(() => editor.updateShapes(updates), { history: 'ignore', ignoreShapeLock: true })
	}

	function highlight(courseId) {
		const edges = graph()
		const chain = new Set([
			...closure(courseId, edges, 'up'),
			...closure(courseId, edges, 'down'),
		])
		const updates = []
		for (const s of courseShapes()) {
			updates.push({ id: s.id, type: s.type, opacity: chain.has(s.id) ? 1 : DIM_BOX })
		}
		for (const [aid, e] of edges) {
			const on = chain.has(e.from) && chain.has(e.to)
			updates.push({ id: aid, type: 'arrow', opacity: on ? 1 : DIM_ARROW })
		}
		setOpacities(updates)
	}

	function reset() {
		const updates = []
		for (const s of courseShapes()) updates.push({ id: s.id, type: s.type, opacity: 1 })
		for (const s of editor.getCurrentPageShapes()) {
			if (s.type === 'arrow') updates.push({ id: s.id, type: 'arrow', opacity: BASE_ARROW })
		}
		setOpacities(updates)
	}

	function handleEvent(info) {
		if (info?.name !== 'pointer_down' || info.button !== 0) return
		if (!editor.isIn('select.idle')) return
		let point = null
		try {
			if (info.point && editor.screenToPage) point = editor.screenToPage(info.point)
		} catch {}
		point ??= editor.inputs?.currentPagePoint
		if (!point) return

		const hit = courseShapes().find((s) => {
			const b = editor.getShapePageBounds(s)
			return b && point.x >= b.x && point.x <= b.x + b.w && point.y >= b.y && point.y <= b.y + b.h
		})
		if (hit) highlight(hit.id)
		else reset()
	}

	try {
		editor.setCurrentTool('select')
	} catch {}
	editor.on('event', handleEvent)
	signal.addEventListener('abort', () => editor.off('event', handleEvent))
}
