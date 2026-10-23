# Security Policy

## Supported versions

Only the latest minor release receives security fixes.

## Reporting a vulnerability

Please do **not** open a public issue. Report privately via GitHub's
[private vulnerability reporting](https://github.com/ZhuchkaTriplesix/mkdocs-dbml/security/advisories/new)
or by email to mrlololoshka94@gmail.com. Include a description, reproduction steps and the affected version.

You can expect an acknowledgement within a few days and a fix or mitigation plan as soon as it is assessed.

## Scope

The plugin reads `.dbml` files from `docs_dir` (path traversal outside it is rejected) and emits static HTML/SVG/JS. Reports about unsanitised DBML content reaching the generated page or reading files outside `docs_dir` are in scope.
