---
name: lucide-react icon names
description: Some icon names don't exist in this project's lucide-react version — known safe replacements.
---

## Rule
`Activity` does not exist in this project's installed version of lucide-react. Using it causes a runtime `ReferenceError` that breaks the Layout component.

**Why:** The lucide-react version pinned in this project predates the `Activity` icon being added.

**How to apply:** Whenever you would use `Activity` from lucide-react, use `BarChart2` instead. It renders fine and is semantically close enough for dashboards and log pages.
