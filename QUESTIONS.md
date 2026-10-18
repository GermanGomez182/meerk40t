# Working assumptions

| # | Question | Working assumption | Why |
| --- | --- | --- | --- |
| Q1 | Does accepting the list authorize all ideas at once? | Deliver a useful slice for each accepted priority, in order. | Maintains reviewable changes without inventing an entire redesign. |
| Q2 | Replace the main layout? | Add an opt-in companion window with normal saved geometry. | Reversible and preserves the user's layout. |
| Q3 | What controller can we rely on? | Use the active Lihuiyu service; show unsupported state for other services and passive/unknown hardware state when unobservable. | The user identified K40/Lihuiyu, but no physical controller is available here. |
| Q4 | What power represents real tube output? | Label it as the controller setting, never measured output. | Avoids implying feedback absent from the data. |
| Q5 | How to store material results? | Local per-device JSON notes in the application work directory; explicit save. | Keeps data local and scoped to the actual machine. |
| Q6 | Which duplicate paths are safe to flag? | Exact identical vector geometry with the same transform; no automatic deletion. | Avoids speculative tolerance and destructive cleanup. |
| Q7 | What performance work is justified? | Profile the new reports on a deterministic synthetic document; optimize only a measured issue. | No speculative code. |
| Q8 | Git integration? | Continue the existing improvement branch and push finished commits to the fork. No upstream PR or merge. | Matches existing authorization. |
| Q9 | What connection state is observable passively? | USB driver's `is_connected()` is a local software-handle getter, not a hardware query. TCP socket presence alone is unverified unless a known connection-status event establishes more. Never open a connection or query controller status for a report. | Reflects the existing CH341/TCP implementations without inventing live hardware feedback. |
| Q10 | How should material notes behave during a device switch? | A separate managed Material Notes window remains bound to the clearly displayed device it opened for. Save uses that device ID; open a new notes window for another device. | Prevents redirecting an unsaved observation to a different machine. |

