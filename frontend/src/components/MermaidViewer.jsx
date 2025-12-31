import { useEffect, useMemo, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false });

export default function MermaidViewer({ chart }) {
  const renderTarget = useRef(null);
  const chartId = useMemo(
    () => `mermaid-${Math.random().toString(36).slice(2, 9)}`,
    []
  );
  const safeChart =
    chart && chart.trim()
      ? chart
      : 'flowchart TD\n  A([No diagram])';

  useEffect(() => {
    let cancelled = false;
    async function render() {
      try {
        const { svg } = await mermaid.render(chartId, safeChart);
        if (!cancelled && renderTarget.current) {
          renderTarget.current.innerHTML = svg;
        }
      } catch (err) {
        if (renderTarget.current) {
          renderTarget.current.innerHTML = `<pre class="mermaid-error">${err.message}</pre>`;
        }
      }
    }
    render();
    return () => {
      cancelled = true;
    };
  }, [safeChart, chartId]);

  return <div className="mermaid-output" ref={renderTarget} />;
}

