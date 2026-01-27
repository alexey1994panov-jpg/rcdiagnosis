// static/timeline.js
import {
  renderTimeline,
  renderTimebar,
  moveSelection,
  updateSelectionHighlight,
  scrollToRow
} from './timeline-render.js';
import { describeFlags } from './timeline-flags.js';
import { updateTrackScheme } from './timeline-scheme.js';

// Экспортируем наружу те же функции, что были раньше
window.renderTimeline = renderTimeline;
window.renderTimebar = renderTimebar;
window.moveSelection = moveSelection;
window.updateSelectionHighlight = updateSelectionHighlight;
window.scrollToRow = scrollToRow;
window.describeFlags = describeFlags;
window.updateTrackScheme = updateTrackScheme;
