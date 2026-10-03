# Subotai: Reliable foundation

Publication status: published on GitHub; board setup completed October 2, 2026.

GitHub is the source of truth for status and future scope changes. The descriptions
below preserve the initial planning notes.

- [Subotai roadmap board](https://github.com/users/VickenM/projects/1/views/1)
- [Reliable foundation milestone](https://github.com/VickenM/Subotai/milestone/1)
- The board is private, linked to the repository, and starts with all 18 issues in Backlog.

| Workstream | Parent issue | Implementation sub-issues |
| --- | --- | --- |
| Architecture and diagrams | [#17](https://github.com/VickenM/Subotai/issues/17) | [#24](https://github.com/VickenM/Subotai/issues/24), [#25](https://github.com/VickenM/Subotai/issues/25) |
| Minimum node dimensions | [#18](https://github.com/VickenM/Subotai/issues/18) | [#26](https://github.com/VickenM/Subotai/issues/26), [#27](https://github.com/VickenM/Subotai/issues/27) |
| JSON persistence | [#19](https://github.com/VickenM/Subotai/issues/19) | [#28](https://github.com/VickenM/Subotai/issues/28), [#29](https://github.com/VickenM/Subotai/issues/29), [#30](https://github.com/VickenM/Subotai/issues/30) |
| Undo/redo | [#20](https://github.com/VickenM/Subotai/issues/20) | [#31](https://github.com/VickenM/Subotai/issues/31), [#32](https://github.com/VickenM/Subotai/issues/32), [#33](https://github.com/VickenM/Subotai/issues/33) |
| Typing and docstrings | [#12](https://github.com/VickenM/Subotai/issues/12), expanded existing issue | [#21](https://github.com/VickenM/Subotai/issues/21), [#22](https://github.com/VickenM/Subotai/issues/22), [#23](https://github.com/VickenM/Subotai/issues/23) |

Repository: https://github.com/VickenM/Subotai

## GitHub organization

- Milestone: **Reliable foundation**, with no deadline until scope is estimated.
- Project: **Subotai roadmap**.
- Board statuses: Backlog, Ready, In progress, Review, Done.
- Use existing labels where appropriate; suggested categories are documentation,
  bug, enhancement, testing, and maintenance.
- Put all five parent issues and their implementation sub-issues in the milestone
  and project. Track implementation status on the sub-issues.
- Review existing issues before publishing; reuse or link overlapping work.
- Link implementation pull requests to their corresponding issues. A parent issue
  closes only when its acceptance criteria and sub-issues are complete.

Suggested sequence: architecture inventory and contracts; node sizing; persistence;
undo/redo; final annotation/docstring coverage audit. Add annotations and docstrings
as each component changes. The locally implemented PySide6 migration is a baseline
dependency and is not assumed to be committed, pushed, or merged.

## Parent: Document Subotai's architecture and behavior with diagrams

### Problem

The project lacks a maintained explanation of its major components, their
responsibilities, and the flows connecting graph editing to automation execution.
Contributors need to understand both the current design and the intended changes.

### Scope

Create Markdown documentation under `docs/`, linked from the README. Describe the
application entry point and window, graph scene/view/items, node registry and
add-ons, node classes, parameters and plugs, event signals, worker/thread ownership,
persistence, and command history. Clearly distinguish current behavior from
proposed architecture. Use Mermaid for diagrams that render directly on GitHub.

### Acceptance criteria

- [ ] A component diagram shows boundaries, dependencies, and ownership.
- [ ] Sequence diagrams explain node creation, connecting nodes, execution,
      saving/loading, and undo/redo.
- [ ] Signal/event flow is distinguished from parameter/data flow.
- [ ] Thread affinity, lifecycle, cancellation, and known limitations are explained.
- [ ] A worked example traces an existing workflow through the relevant code.
- [ ] Custom-node documentation explains registration and required contracts.
- [ ] Links resolve and diagrams render on GitHub.
- [ ] Documents are updated alongside persistence and undo/redo changes.

### Proposed sub-issues

1. **Map current components, state ownership, and execution lifecycle** — inventory
   the modules and public contracts; document actual behavior and known gaps.
2. **Write the architecture guide and Mermaid diagrams** — publish the overview,
   sequence diagrams, worked example, and extension guide; link from README.

## Parent: Enforce content-based minimum node dimensions

### Problem

Nodes can be reduced to a tiny square, hiding plugs and other child items. Users
must manually expand them before the node is usable.

### Scope

Calculate minimum dimensions from titles, input/output plug counts and labels,
spacing, padding, and other child items. Apply the same constraints to initial
layout, interactive resizing, programmatic changes, loading, and undo/redo.

### Acceptance criteria

- [ ] Every node initially fits all required child items without overlap or clipping.
- [ ] Dragging the resizer cannot make the node smaller than its content requires.
- [ ] Dynamic plugs, renaming, and font changes recompute the minimum size.
- [ ] Longer opposing input/output labels cannot overlap.
- [ ] Existing valid user sizes are preserved; undersized legacy sizes are enlarged.
- [ ] Size normalization is deterministic and documented in persistence behavior.
- [ ] Tests cover asymmetric plug counts, long labels, dynamic plugs, empty nodes,
      high-DPI/font metrics, save/load, and resize undo/redo.

### Proposed sub-issues

1. **Centralize node content measurement and size constraints** — introduce a
   single layout calculation and apply it to construction and resize paths.
2. **Integrate dynamic sizing, legacy graph loading, and regression tests** — cover
   content changes and restored sizes, and verify representative nodes visually.

## Parent: Make JSON graph persistence accurate, validated, and maintainable

### Problem

Graph loading and saving combine multiple responsibilities and duplicate logic.
The existing examples alone cannot establish complete preservation of graph state.

### Scope

Retain JSON. Define a versioned document model and separate model-to-document
conversion, JSON encoding/decoding, validation, migration, and scene construction.
Inventory persistent state for every built-in node and define how add-ons provide
additional state. Use shared helpers for load and clipboard operations while
preserving their different identity semantics.

### Acceptance criteria

- [ ] A documented schema represents node IDs/types, parameters and explicit
      defaults, enabled state, names, positions, sizes, connections, groups, and
      any other state identified by the inventory.
- [ ] Transient widgets, threads, processes, and runtime handles are excluded with
      explicit reconstruction rules. Image/queue/custom parameter policies are defined.
- [ ] Save/load preserves semantic graph state and stable IDs; paste creates new
      IDs and correctly remaps internal connections.
- [ ] Dynamic plugs restore deterministically without edge-order assumptions.
- [ ] Old example files remain readable through explicit compatibility rules.
- [ ] Unknown node types, missing add-ons, malformed parameters, invalid endpoints,
      duplicate IDs, and unsupported schema versions yield actionable errors.
- [ ] Failed loading leaves the current graph intact; failed saving does not
      overwrite a valid existing file with a partial document.
- [ ] Restoring a document does not inadvertently execute its automation; enabled
      state and activation timing have an explicit, tested contract.
- [ ] Tests compare complete semantic state, not just counts, across save/load/save.
- [ ] The only intentional normalizations, such as minimum node sizes, are
      documented and produce a stable result after the first migration.

### Proposed sub-issues

1. **Inventory graph state and define the versioned JSON contract** — specify IDs,
   node/plug types, values, extension points, transient state, and compatibility.
2. **Separate serialization, validation, migration, and scene reconstruction** —
   remove duplicated loading logic; implement safe save/load and clipboard ID rules.
3. **Add exhaustive persistence and legacy compatibility tests** — test all built-in
   types, representative add-on state, dynamic plugs, malformed documents, and
   repeated round trips with non-default values.

Dependencies: architecture/state inventory; coordinate node-size normalization
with the minimum-size workstream.

## Parent: Make graph editing undo/redo deterministic and reliable

### Problem

Undo/redo has historically been unreliable. Users must be able to trust that edits
can be reversed and replayed without losing graph state or corrupting connections.

### Scope

Audit commands for create/delete, connect/disconnect/reconnect, move, resize,
rename, parameter edits, grouping, and copy/paste. Specify command ownership,
object lifetime, selection restoration, merging, and transaction boundaries.
Reuse the persistent state contracts where appropriate without making a disk
serialization round trip a prerequisite for every edit.

### Acceptance criteria

- [ ] Undo restores the exact preceding persistent state; redo restores the exact
      resulting state, with explicit rules for selection and other editor state.
- [ ] Deleting/restoring nodes preserves parameters, IDs, groups, and all edges.
- [ ] Dynamic plugs and connection replacement survive repeated undo/redo.
- [ ] Dragging, typing, and multi-item actions have useful, documented undo granularity.
- [ ] Undoing and then making a new edit correctly discards the abandoned redo branch.
- [ ] Failed/no-op commands do not corrupt history or create misleading entries.
- [ ] New/open/save operations have correct history boundaries and dirty-state behavior.
- [ ] Qt/Python object ownership does not leave deleted wrappers or stale references.
- [ ] Restoring history does not accidentally execute external automation.
- [ ] Sequence tests cover create → connect → edit → group → delete → undo all →
      redo all → save → reload, asserting full semantic state at each boundary.

### Proposed sub-issues

1. **Audit command semantics and add reproductions for undo/redo failures** —
   document contracts and build regression cases before changing behavior.
2. **Repair command state restoration, ownership, and edit transactions** — implement
   consistent behavior for graph edits, dynamic plugs, grouped actions, and merging.
3. **Verify history branching, dirty state, and long edit sequences** — exercise
   repeated undo/redo, document boundaries, failure cases, and persistence together.

Dependencies: shared graph state contract from persistence. Failure reproductions
and command auditing can begin before the persistence refactor is complete.

## Parent: Add modern type annotations and useful docstrings throughout the codebase

### Problem

The project's interfaces and state contracts are difficult to infer from largely
untyped, sparsely documented code. Coverage must include the whole project, not
only recently modified modules.

### Scope

Annotate project-owned Python modules, classes, functions, methods, and meaningful
state, including the application, graph library, UI, built-in nodes, and tests.
Use syntax compatible with the supported Python minimum. Document contracts,
side effects, exceptions, thread requirements, and serialization responsibilities.

### Acceptance criteria

- [ ] A consistent annotation/docstring convention and configured type checker exist.
- [ ] Qt overrides and signal/slot interfaces use accurate compatible signatures.
- [ ] Parameter and node interfaces use meaningful types rather than blanket `Any`.
- [ ] Unavoidable third-party typing exceptions are narrow and justified.
- [ ] Every project-owned module/class/function/method is reviewed for annotation
      and docstring coverage; exclusions are explicit and justified.
- [ ] Documentation explains behavior and constraints, not just names or signatures.
- [ ] Type checks and regression tests pass on the supported development baseline.
- [ ] Typing/docstring-only changes preserve behavior; functional fixes are identified
      and tested separately.

### Proposed sub-issues

1. **Establish typing conventions, checker configuration, and a coverage inventory** —
   choose checker settings, docstring style, Qt conventions, and measurable coverage.
2. **Annotate and document the application, graph library, and UI** — cover state,
   persistence, commands, scenes/views/items, and thread-facing interfaces.
3. **Annotate and document all built-in nodes, extension contracts, and tests** —
   complete the inventory and enable the agreed checks in CI.

Dependencies: do incremental annotations/docstrings alongside each refactor; run
the final completeness audit after persistence and history interfaces stabilize.
