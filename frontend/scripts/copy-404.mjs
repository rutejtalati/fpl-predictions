import { copyFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

function copy404Fallback() {
  const distDir = resolve(process.cwd(), "dist");
  const indexPath = resolve(distDir, "index.html");
  const notFoundPath = resolve(distDir, "404.html");

  if (!existsSync(indexPath)) {
    throw new Error("dist/index.html not found. Run build before postbuild.");
  }

  copyFileSync(indexPath, notFoundPath);
  console.log("Copied dist/index.html -> dist/404.html");
}

copy404Fallback();
