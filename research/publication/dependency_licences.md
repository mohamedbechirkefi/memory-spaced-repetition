<!-- SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Every installed Python package (read from the `.venv` package metadata after `uv sync --frozen --all-groups --all-extras`; `License-Expression`, else the licence text or classifier) and every npm package of the demo (read from `demo/node_modules/*/package.json`; for platform-specific optional packages not installed on this machine, the `license` field of `demo/package-lock.json`). The project itself is under `LicenseRef-MEMORY-NC-Research-1.0` (see `LICENSE`) and is not listed. Runtime means needed to run the simulator or to load the built page; development means tests, type checks or the build.

**Result: no package outside the permissive set (MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0 or similar) was found. Nothing is flagged.** Notes: MPL-2.0 (hypothesis, lightningcss) is a file-level weak copyleft licence, used here only as a development tool and not modified or redistributed; `pillow` is MIT-CMU (a permissive historical licence); `numpy` bundles code under BSD-3-Clause, 0BSD, MIT, Zlib and CC0-1.0, all permissive; `tslib` is 0BSD. The built page (`demo/dist`) bundles only React, React DOM and scheduler (all MIT).

## Python (`uv.lock`)

| package | version | licence | use |
|---|---|---|---|
| attrs | 26.1.0 | MIT | runtime |
| contourpy | 1.4.0 | BSD-3-Clause | runtime |
| cycler | 0.12.1 | BSD-3-Clause (licence text; classifier BSD License) | runtime |
| fonttools | 4.68.0 | MIT | runtime |
| hypothesis | 6.170.15 | MPL-2.0 | development (tests) |
| iniconfig | 2.3.1 | MIT | development (tests) |
| jsonschema | 4.26.0 | MIT | runtime |
| jsonschema-specifications | 2025.9.1 | MIT | runtime |
| kiwisolver | 1.5.1 | BSD-3-Clause (licence text; classifier BSD License) | runtime |
| matplotlib | 3.11.2 | PSF-based matplotlib licence (classifier Python Software Foundation License) | runtime |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | runtime |
| pillow | 13.0.0 | MIT-CMU | runtime |
| pluggy | 1.7.0 | MIT | development (tests) |
| Pygments | 2.21.0 | BSD-2-Clause | development (tests) |
| pyparsing | 3.3.3 | MIT | runtime |
| pytest | 9.2.0 | MIT | development (tests) |
| python-dateutil | 4.0.0 | BSD-3-Clause | runtime |
| referencing | 0.37.0 | MIT | runtime |
| rpds-py | 2026.9.1 | MIT | runtime |
| sortedcontainers | 2.4.0 | Apache-2.0 | development (tests) |
| typing_extensions | 4.16.0 | PSF-2.0 | runtime |
| tzdata | 2026.6 | Apache-2.0 | runtime |

## npm (`demo/package-lock.json`)

| package | version | licence | use |
|---|---|---|---|
| @emnapi/core | 2.0.0-beta.2 | MIT | development (lockfile; not installed on this platform) |
| @emnapi/runtime | 2.0.0-beta.2 | MIT | development (lockfile; not installed on this platform) |
| @emnapi/wasi-threads | 2.2.0 | MIT | development (lockfile; not installed on this platform) |
| @jridgewell/sourcemap-codec | 1.6.0 | MIT | development |
| @napi-rs/wasm-runtime | 1.2.6 | MIT | development (lockfile; not installed on this platform) |
| @oxc-project/types | 0.156.0 | MIT | development |
| @rolldown/binding-android-arm-eabi | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-android-arm64 | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | development |
| @rolldown/binding-darwin-x64 | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-freebsd-x64 | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-arm-gnueabihf | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-arm64-gnu | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-arm64-musl | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-ppc64-gnu | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-s390x-gnu | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-x64-gnu | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-linux-x64-musl | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-openharmony-arm64 | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-wasm32-wasi | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-win32-arm64-msvc | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/binding-win32-x64-msvc | 1.2.19 | MIT | development (lockfile; not installed on this platform) |
| @rolldown/pluginutils | 1.1.1 | MIT | development |
| @standard-schema/spec | 1.1.0 | MIT | development |
| @tybys/wasm-util | 0.10.5 | MIT | development (lockfile; not installed on this platform) |
| @types/chai | 5.2.3 | MIT | development |
| @types/deep-eql | 4.0.2 | MIT | development |
| @types/estree | 1.0.11 | MIT | development |
| @types/react | 19.3.0 | MIT | development |
| @types/react-dom | 19.3.0 | MIT | development |
| @vitejs/plugin-react | 6.1.2 | MIT | development |
| @vitest/expect | 4.1.12 | MIT | development |
| @vitest/mocker | 4.1.12 | MIT | development |
| @vitest/pretty-format | 4.1.12 | MIT | development |
| @vitest/runner | 4.1.12 | MIT | development |
| @vitest/snapshot | 4.1.12 | MIT | development |
| @vitest/spy | 4.1.12 | MIT | development |
| @vitest/utils | 4.1.12 | MIT | development |
| assertion-error | 2.0.1 | MIT | development |
| chai | 6.3.0 | MIT | development |
| convert-source-map | 2.0.0 | MIT | development |
| csstype | 3.2.4 | MIT | development |
| detect-libc | 2.1.2 | Apache-2.0 | development |
| es-module-lexer | 2.3.2 | MIT | development |
| estree-walker | 3.0.3 | MIT | development |
| expect-type | 1.4.0 | Apache-2.0 | development |
| fdir | 6.5.0 | MIT | development |
| fsevents | 2.3.3 | MIT | development |
| lightningcss | 1.33.0 | MPL-2.0 | development |
| lightningcss-android-arm64 | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | development |
| lightningcss-darwin-x64 | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-freebsd-x64 | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-linux-arm-gnueabihf | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-linux-arm64-gnu | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-linux-arm64-musl | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-linux-x64-gnu | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-linux-x64-musl | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-win32-arm64-msvc | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| lightningcss-win32-x64-msvc | 1.33.0 | MPL-2.0 | development (lockfile; not installed on this platform) |
| magic-string | 0.30.21 | MIT | development |
| nanoid | 3.3.20 | MIT | development |
| obug | 2.2.1 | MIT | development |
| pathe | 2.0.3 | MIT | development |
| picocolors | 1.1.1 | ISC | development |
| picomatch | 4.0.7 | MIT | development |
| postcss | 8.5.33 | MIT | development |
| react | 19.3.1 | MIT | runtime |
| react-dom | 19.3.1 | MIT | runtime |
| rolldown | 1.2.19 | MIT | development |
| scheduler | 0.28.0 | MIT | runtime |
| siginfo | 2.0.0 | ISC | development |
| source-map-js | 1.2.4 | BSD-3-Clause | development |
| stackback | 0.0.2 | MIT | development |
| std-env | 4.3.0 | MIT | development |
| tinybench | 2.9.0 | MIT | development |
| tinyexec | 1.4.0 | MIT | development |
| tinyglobby | 0.2.17 | MIT | development |
| tinyrainbow | 3.2.0 | MIT | development |
| tslib | 2.9.1 | 0BSD | development (lockfile; not installed on this platform) |
| typescript | 5.9.3 | Apache-2.0 | development |
| vite | 8.3.5 | MIT | development |
| vitest | 4.1.12 | MIT | development |
| why-is-node-running | 2.3.0 | MIT | development |

Tools outside the repository (pandoc 3.6.3, GPL-2.0-or-later as stated by the pandoc project, not printed by `pandoc --version`; the `typst` Python package 0.15.0, Apache-2.0 from its metadata; Node 22, MIT as stated by the Node.js project) are used as external programs and are not bundled or redistributed.
