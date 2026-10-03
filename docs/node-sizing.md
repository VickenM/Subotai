# Node sizing

`PywerNode.minimumSize()` measures the current content in Qt scene coordinates.
It reserves the header and spinner, the width of the editable caption, both plug
columns, the tallest shape/font in each row, a gap between columns and a bottom
margin for the resize handle. Measurement and painting share `content_font`.
The editable caption retains its existing placement above the node body.

`setSize()` clamps requested dimensions to that minimum and updates plug, label,
spinner, resize-handle and edge positions. Interactive resize delegates to it;
file loading, paste and resize undo/redo already use the same entry point.
`adjust()` reapplies the current size after content changes. Adding/removing plugs
and editing the caption invoke it automatically. Extensions that change plug
labels, `content_font`, or other embedded graphics should call `adjust()` after
the change. Additional children at nonnegative positions contribute their right
and bottom bounds; their internal layout remains the extension's responsibility.

Nodes grow when content requires it but do not automatically shrink when content
is removed. Users can shrink them to the new minimum. Sizes larger than the
minimum survive layout updates, loading and history replay, including height.

Legacy JSON sizes below the minimum are enlarged on reconstruction. Saving writes
the resulting normalized size; opening that saved graph retains it. The JSON
format does not change. A requested undersized history value is likewise clamped
to the content present when it is replayed.

[`tests/test_node_sizing.py`](../tests/test_node_sizing.py) checks containment,
nonoverlapping labels, uneven columns, long names, larger fonts, embedded items,
dynamic plug history/reconstruction, edge updates, direct/handle resizing, all
three reconstruction paths and size round trips. The existing integration suite
also checks plug/label containment for every built-in node type.
