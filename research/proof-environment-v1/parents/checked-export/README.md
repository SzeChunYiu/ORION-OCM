# Checked-map exporter adapter

Mechanically derived from the pinned Apache-2.0 parent Export.lean (see ../lean4export/LICENSE). Original remains unchanged. ADAPTATION.json gives exact source and transformation.

Lean 4.33.1 replay returns an Environment.ofKernelEnv whose checked constants can be absent from the elaborator lookup tables. This adapter changes only the three exporter environment type annotations to Kernel.Environment, reuses the parent JSON definitions, and adds a namespace. All 407 copied parent lines retain the same NDJSON construction. This avoids adding unchecked declarations merely to support serialization. The bridge independently parses and compares its output before PREPARED.
