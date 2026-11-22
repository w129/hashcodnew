# Openicons by Hashcod — Full Offline Windows

This is an independent, isolated build branch of Openicons by Hashcod. The main branch of Hashcod Codespace is unaffected.

The workflow `openicons-full-windows.yml` downloads the official `@iconify/json` dataset **during CI**, validates *actual SVG data*, bundles every accepted collection into the Go executable, compiles for Windows x64, runs smoke tests and uploads an EXE and ZIP.

The build **fails instead of claiming success** if fewer than 300,000 searchable names or fewer than 150 complete icon sets are present. The EXE does not require the Iconify API to search or render its bundled icons.

Original source: Openicons by Hashcod v5, which runs a local Go server and opens a browser app window. It does **not** guarantee the original logo on Windows taskbar: browser-managed app windows may show the browser icon.

SVG sets have independent licenses and some require attribution; check the per-collection metadata. This application is not affiliated with Iconify. The catalog includes aliases, which are not necessarily unique drawings.

The compressed source archive is `tools/openicons-full/source.tar.gz`. All build and test logic is public within this branch's source files. GitHub Actions artifacts are stored in the connected repository.
