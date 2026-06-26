# Node.js Adapter

The Node.js adapter detects JavaScript/TypeScript projects and generates reproduction plans.

## Detection

Files detected:
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `*.js`, `*.ts`, `index.js`, `main.js`, `scripts/*.js`, `scripts/*.ts`

## Planning

Install steps (by lock file priority):
- `pnpm-lock.yaml` → `pnpm install`
- `yarn.lock` → `yarn install`
- `package-lock.json` → `npm ci`
- `package.json` → `npm install`

Run steps:
- `node <script>` for JavaScript files

## Runtime

Requires: `node`

Support level: **execute-if-runtime-present**

## Limitations

- Node.js runtime must be installed separately
- npm install may download many packages
