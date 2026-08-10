---
tags: [inbox]
---

# Inbox

> Dump everything here first. Process weekly — move each item to Projects, Areas, Resources, or Archive.

## Unprocessed
- **2026-08-10 — Madonna Mani Basse 3MF: added gold crown, prepped for Bambu H2S.** Uploaded Bambu Studio project (`madonnamanibasse.3mf`, 4 plates at 200/150/100/50mm statue height) had no crown geometry and was targeting a Bambu Lab P1S. Added a procedurally modeled 5-point "small gold crown" (watertight mesh, sized proportionally to the statue's head on each plate, embedded into the veil for a solid bond) as a separate part assigned to the existing gold filament slot (#FEC600, extruder 3) so it prints via AMS color-swap alongside the white statue — no glue needed. Switched printer profile to Bambu Lab H2S (0.4mm nozzle, 340×320×325mm build volume). Kept all 4 filament slots defined (didn't risk hand-trimming the array) but only slots 1 (white) and 3 (gold) are actually used, so no extra purge. Finished file delivered directly to the user (not committed here — 22MB binary, out of scope for a notes vault). Note: the 50mm plate's crown is only ~4.6mm across — spikes may partially blob at that scale; 100mm+ prints the detail cleanly. **Update:** first crown design was too plain (5 bare cones); redesigned as a proper jeweled crown (beaded band trim, 5 tall pearl-topped fleur points alternating with 5 short merlons) after user review of rendered mockups. Final design approved and baked into all 4 plates. **Bug fix:** crown wasn't showing up when opened in Bambu Studio — root cause was an internal object-ID collision (both the statue's mesh file and the crown's mesh file used id="1" internally; some 3MF parsers key components by ID alone, not by file path, so the crown component silently resolved to the statue mesh instead). Gave the crown mesh a distinct internal id (500), re-verified with an independent 3MF parser (not just my own code) that the file now contains 2 distinct geometries and 8 correctly-scaled instances, and re-sent the corrected file.

---

*Empty inbox = clear mind.*
