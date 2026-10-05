import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

// Explicit course folders only. No drive-wide discovery, no deletions, no overwrites.
const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argumentsList = process.argv.slice(2);
const apply = argumentsList.includes('--apply');
const refreshManifest = argumentsList.includes('--refresh-manifest');
const sourceIndex = argumentsList.indexOf('--source-root');
const sourceBase = sourceIndex >= 0 ? argumentsList[sourceIndex + 1] : undefined;
const verify = argumentsList.includes('--verify');
const groups = [
  { id: 'web-lab2', source: 'web-pro/lab2/Lab2', target: 'WebProgramming/Lab2', title: 'Web Lab2：Servlet / JSP 源码', description: '保留 Servlet 控制器、区域判断与 HitResult 模型、JSP、浏览器 JS/CSS 和 Gradle WAR 工程。构建描述声明 Java 11、Jakarta Servlet 6.0 / JSP 3.1。', requirements: '需要 JDK、Gradle Wrapper 以及兼容 Jakarta Servlet 的应用服务器。服务器发行包和字体未导入。' },
  { id: 'web-lab3', source: 'web-pro/Lab3', target: 'WebProgramming/Lab3/local-source', title: 'Web Lab3：JSF / JPA / JMX 源码快照', description: '保留 JSF / PrimeFaces 页面、PointBean / ResultBean、EclipseLink 实体、区域判断测试和 JMX MBean。现有 Lab3 学习笔记继续作为课程入口。', requirements: '原始数据库连接、persistence.xml、build.properties 和应用服务器未导入；需自行建立公开配置示例后再验证构建/部署。' },
  { id: 'web-lab4', source: 'web-pro/Lab4', target: 'WebProgramming/Lab4/local-source', title: 'Web Lab4：Spring Boot / React 源码快照', description: '保留 Java 17 / Spring Boot 3.2 后端与 React 19 / Redux Toolkit 前端源码、公开资源和 npm 包锁文件。后端 static 目录中的前端打包产物未导入。', requirements: 'Java 树下的 SecurityConfig 已保留；原始 application.properties、Compose 和服务器发行包未导入。需要补齐数据库环境，并先核对原 Gradle Wrapper 9.2.1 与 Spring Boot 3.2.0 的构建兼容性。' },
  { id: 'web-opi-variant', source: 'web-pro/lab3-opi4', target: 'WebProgramming/Lab3/opi-variant', title: 'Web Lab3 / OPI Lab4：历史源码变体', description: '这是与主 Lab3 不同的 JSF / MBean 版本，保留原有相对位置；其 MBean Java 位于 WEB-INF/mbean。它不替代主 Lab3 或 OPI 现有实现。', requirements: 'HttpUnit 工具副本、报告、服务器发行包和数据库配置未导入。Java 源目录与 MBean 编译关系尚未验证。' },
  { id: 'prolang-work8', source: 'ProLang/class8', target: 'ProgrammingLanguage/work8', title: 'Work8：反射、Attribute 与动态 IL', description: '真实 .NET 8 控制台项目：扫描程序集中的自定义 Attribute、按触发器和优先级注册技能、通过 MethodInfo.Invoke 执行；Performance/EmitDemo.cs 另含 DynamicMethod / IL 生成示例，但当前 Main 没有调用它。', requirements: '需要 .NET 8 SDK。可在此目录运行 dotnet run --project class8.csproj；本次没有运行或进行性能测试。' },
  { id: 'prolang-class01', source: 'ProLang/class01', target: 'ProgrammingLanguage/local-variants/class01', novel: true, codeOnly: true, title: '早期 C / C++ 源码变体', description: '保留仓库未收录的 C / C++ 学习源码，原文件夹层级用于区分多个早期版本。', requirements: '只保存新增源码，不复制 IDE 工程、编译产物或完全重复代码；需要按单个练习选择编译入口。' },
  { id: 'prolang-class1', source: 'ProLang/class1', target: 'ProgrammingLanguage/local-variants/class1', novel: true, codeOnly: true, title: 'Class1：C 源码变体', description: '保留早期 C 函数、库头文件和示例源码。', requirements: '只保存新增源码；不代表一套已验证的完整工程。' },
  { id: 'prolang-class2', source: 'ProLang/class2', target: 'ProgrammingLanguage/local-variants/class2', novel: true, codeOnly: true, title: 'Class2：C / C++ 源码变体', description: '保留仓库未收录的 C / C++ 示例，不覆盖 work2。', requirements: '需要分别选择 C 或 C++ 入口编译；原 IDE 工程未导入。' },
  { id: 'prolang-class3', source: 'ProLang/class3', target: 'ProgrammingLanguage/local-variants/class3', novel: true, title: 'Class3：角色战斗 .NET 源码变体', description: '保留 BattleManager、Legend、Garen、Mantis 和控制台入口的另一套实现。', requirements: '需要 .NET 8 SDK；与 work3 的已有实现并存，尚未构建。' },
  { id: 'prolang-class5', source: 'ProLang/class5', target: 'ProgrammingLanguage/local-variants/class5', novel: true, codeOnly: true, rootOnly: true, title: 'Class5：服务实现源码变体', description: '保留根目录下未收录的 PageAggregatorService / SlowExternalDataService 变体。', requirements: '接口与标准项目见现有 work5；此目录只保存新增片段，不能单独运行。外部电影数据集和其他大数据未重复导入。' },
  { id: 'prolang-native', source: 'ProLang/fast_lib', target: 'ProgrammingLanguage/local-variants/fast_lib', novel: true, codeOnly: true, title: 'C Native Library 源码变体', description: '保留另一份 native library C / 头文件源码。', requirements: '不复制 DLL、LIB、OBJ、PDB 或 IDE 用户状态；需自行选定编译器与调用方验证接口。' },
  { id: 'math-lab1', source: 'ComputationalMath/Lab1', target: 'ComputationalMath/Lab1/local-variant', title: '计算数学 Lab1：简单迭代法源码变体', description: '入口标明变体 15；保留简单迭代求解、对角占优行排列、残差输出，以及 test1–6 输入。Main、FormulaUtils、MatrixPrinter、SimpleIteration 与已有版本不同，原 src 保持原样。', requirements: '需要 JDK 与 Gradle Wrapper。算法停止准则为相邻迭代变化小于 eps，不能据此声称已验证全部收敛情况。' },
  { id: 'algo-lab1', source: 'algo/Lab1/LabsAlgorithm', target: 'AADS/local-lab1', pattern: /^part(?:9|1[0-6])\.(?:cpp|h)$/, title: '算法 Lab1：part9–16 独立源码', description: '补充原仓库没有的 part9–16。每个 cpp 都有独立 main，因此必须分别编译。', requirements: '部分源码使用 bits/stdc++.h，建议 GCC / Clang 兼容工具链。示例：g++ -std=c++20 part9.cpp -o part9。没有复制将多个 main 链接在一起的原 CMake 文件。' },
  { id: 'information-lab1', source: 'InfoSystem/Lab1', target: 'InformationSystem/Lab1/local-variant', title: '信息系统 Lab1：独立本地源码版本', description: '保留另一份 Spring / EclipseLink 应用源码、原有 docs 与可编辑 UML 图。大量同名 Java / 前端文件与当前 Lab1/Lab1 不同，因此整份独立保存。PROJECT_README.md（若通过检查）为此版本原说明。', requirements: 'Java 树下 JsonConfig、PersistenceConfig、SecurityConfig 已保留。原运行 config、application.yml、Compose 和本地数据库创建配置未导入；资料可能仍描述原部署环境。此版本尚未构建、运行或验收，不覆盖已存在项目。' },
];

const skipDirectory = /^(?:\.git|node_modules|bin|obj|target|dist|build|out|\.gradle|\.idea|\.vs|\.venv|venv|__pycache__|\.tools|\.work|coverage|\.stack-work|cmake-build.*|x64|debug|release|wildfly.*|HttpUnit|\.packages|\.python_deps|credentials|secrets)$/i;
const skipFile = /(?:^\.env(?:\.|$)|credential|secret|(?:^|[._-])token(?:[._-]|$)|private|id_rsa|id_ed25519|\.ppk$|\.pem$|\.key$|keystore|truststore|^application(?:-[^.]+)?\.(?:properties|ya?ml|json)$|^build\.properties$|^docker-compose\.|^compose\.|^persistence\.xml$|^context\.xml$|^standalone\.xml$|^psql-dev\.txt$|^create-local-db\.sql$|^DEPLOYMENT_|^LOCAL_DATABASE_|^.*\.user$|^.*\.iml$|^~\$)/i;
const allowedExtensions = new Set(['.c', '.h', '.cpp', '.hpp', '.cs', '.csproj', '.sln', '.py', '.java', '.js', '.ts', '.jsx', '.tsx', '.html', '.xhtml', '.jsp', '.css', '.scss', '.json', '.xml', '.sql', '.s', '.asm', '.yaml', '.yml', '.md', '.txt', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.drawio', '.gradle', '.bat', '.sh', '.lock']);
const sourceExtensions = new Set(['.c', '.h', '.cpp', '.hpp', '.cs', '.py', '.java', '.js', '.ts', '.s', '.asm']);
const binaryExtensions = new Set(['.png', '.jpg', '.jpeg', '.webp', '.jar']);
const digest = buffer => crypto.createHash('sha256').update(buffer).digest('hex');
const contained = (base, file) => { const relative = path.relative(base, file); return relative === '' || (!path.isAbsolute(relative) && relative !== '..' && !relative.startsWith(`..${path.sep}`)); };
const realPlaceholder = value => /(?:\$\{|\$\(|process\.env|System\.getenv|env\.|<[^>]+>|YOUR_|CHANGE_ME|REPLACE_|EXAMPLE|placeholder|password_here|username_here|\*{3,})/i.test(value);
function suspiciousContent(buffer) {
  const text = buffer.toString('utf8');
  if (/-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----|PuTTY-User-Key-File-|\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|\bAKIA[0-9A-Z]{16}\b/.test(text)) return true;
  const patterns = [
    /\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|PGPASSWORD)["']?\s*[:=]\s*["']([^"'\r\n]{3,})["']/gi,
    /\b(?:password|passwd|pwd|PGPASSWORD|spring\.datasource\.password)\s*[:=]\s*([^\s"'`;<>]{3,})/gi,
    /name\s*=\s*["'][^"']*(?:password|passwd|secret)[^"']*["'][^>]*value\s*=\s*["']([^"']+)["']/gi,
    /\bjdbc:[^\s"']+[?;&]password=([^&;\s"']+)/gi,
  ];
  for (const regex of patterns) for (const match of text.matchAll(regex)) {
    const value = match[1];
    const surroundingLine = text.slice(0, match.index).split(/\r?\n/).at(-1) + text.slice(match.index).split(/\r?\n/)[0];
    const translationArray = /^\s*["'][^"']+["']\s*:\s*\[\s*["'][^"']*["']\s*,\s*["'][^"']*["']\s*\],?\s*$/.test(surroundingLine);
    const autocompleteValue = /\.autocomplete\s*=/.test(surroundingLine) && /^(?:current-password|new-password)$/.test(value);
    if (!realPlaceholder(value) && !translationArray && !autocompleteValue && !/^(?:null|false|true|request\.|user\.|this\.|body\.|data\.|result\.|values\.|password\b|passwd\b|pwd\b|String\b|int\b|long\b|boolean\b)/i.test(value)) return true;
  }
  return false;
}

async function collect(directory, callback, relative = '') {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  entries.sort((a, b) => a.name.localeCompare(b.name));
  for (const entry of entries) {
    const rel = relative ? `${relative}/${entry.name}` : entry.name;
    const absolute = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) { await callback({ relative: rel, excluded: 'symlink' }); continue; }
    if (entry.isDirectory()) {
      const privateConfig = /^config$/i.test(entry.name) && !/(?:^|\/)src\/(?:main|test)\/java\//i.test(rel);
      if (skipDirectory.test(entry.name) || privateConfig) { await callback({ relative: rel, excluded: 'dependency/build/private configuration directory' }); continue; }
      await collect(absolute, callback, rel);
    } else if (entry.isFile()) await callback({ relative: rel, absolute });
  }
}

async function verifyManifests() {
  let totalFiles = 0, totalBytes = 0;
  for (const group of groups) {
    const target = path.resolve(repository, group.target);
    const manifestFile = path.join(target, 'import-manifest.json');
    try {
      const manifest = JSON.parse(await fs.readFile(manifestFile, 'utf8'));
      for (const file of manifest.files) {
        const destination = path.resolve(target, file.path);
        if (!contained(target, destination)) throw new Error(`Manifest path escapes snapshot: ${group.id}`);
        const buffer = await fs.readFile(destination);
        if (digest(buffer) !== file.sha256 || buffer.length !== file.bytes) throw new Error(`Checksum mismatch: ${group.target}/${file.path}`);
        totalFiles++; totalBytes += buffer.length;
      }
    } catch (error) {
      if (error.code === 'ENOENT' && !(await fs.stat(target).catch(() => null))) continue;
      throw error;
    }
  }
  console.log(JSON.stringify({ mode: 'verify', totalFiles, totalBytes, result: 'all imported hashes match' }, null, 2));
}

async function main() {
  if (verify) return verifyManifests();
  if (!sourceBase) { console.log('Usage: node tools/import-local-labs.mjs --source-root <directory containing course folders> [--apply]\nDefault is dry-run. Verify saved copies: --verify'); return; }
  const base = await fs.realpath(path.resolve(sourceBase));
  const duplicateHashes = new Set();
  await collect(path.join(repository, 'ProgrammingLanguage'), async entry => {
    if (entry.excluded || !sourceExtensions.has(path.extname(entry.relative).toLowerCase()) || /^(?:local-variants|work8)\//.test(entry.relative)) return;
    duplicateHashes.add(digest(await fs.readFile(entry.absolute)));
  });
  const plans = [];
  for (const group of groups) {
    const root = path.resolve(base, group.source);
    const target = path.resolve(repository, group.target);
    if (!contained(base, root) || !contained(repository, target)) throw new Error(`Unsafe path: ${group.id}`);
    const rootReal = await fs.realpath(root).catch(() => null);
    if (!rootReal || !contained(base, rootReal)) throw new Error(`Missing or redirected explicit source: ${group.id}`);
    const files = [], excluded = [];
    await collect(root, async entry => {
      if (entry.excluded) { excluded.push({ path: entry.relative, reason: entry.excluded }); return; }
      const basename = path.basename(entry.relative);
      const extension = path.extname(basename).toLowerCase();
      if (/^HELP\.md$/i.test(basename)) { excluded.push({ path: entry.relative, reason: 'generated framework helper' }); return; }
      if (skipFile.test(basename) || /^backend\/src\/main\/resources\/static(?:\/|$)/i.test(entry.relative)) { excluded.push({ path: entry.relative, reason: 'private/deployment configuration or generated frontend bundle' }); return; }
      if (group.pattern && !group.pattern.test(entry.relative)) return;
      if (group.rootOnly && entry.relative.includes('/')) return;
      if (group.codeOnly && !sourceExtensions.has(extension)) return;
      const specialName = /^(?:gradlew|gradle-wrapper\.properties|gradle-wrapper\.jar|CMakeLists\.txt|Dockerfile|Makefile|\.gitignore|\.gitattributes|\.editorconfig)$/i.test(basename);
      if (!allowedExtensions.has(extension) && !specialName) { excluded.push({ path: entry.relative, reason: 'outside explicit source/document whitelist' }); return; }
      const buffer = await fs.readFile(entry.absolute);
      if (!buffer.length) { excluded.push({ path: entry.relative, reason: 'empty file' }); return; }
      if (!binaryExtensions.has(extension) && suspiciousContent(buffer)) { excluded.push({ path: entry.relative, reason: 'suspected credential literal; content not printed' }); return; }
      const sha256 = digest(buffer);
      if (group.novel && duplicateHashes.has(sha256)) { excluded.push({ path: entry.relative, reason: 'already present exact source duplicate' }); return; }
      const outputRelative = entry.relative.toLowerCase() === 'readme.md' ? 'PROJECT_README.md' : entry.relative;
      const destination = path.resolve(target, outputRelative);
      if (!contained(target, destination)) throw new Error(`Unsafe target: ${group.id}/${outputRelative}`);
      const existing = await fs.readFile(destination).catch(error => { if (error.code === 'ENOENT') return null; throw error; });
      if (existing && digest(existing) !== sha256) throw new Error(`Refusing to overwrite different file: ${group.target}/${outputRelative}`);
      files.push({ path: outputRelative, source: entry.relative, bytes: buffer.length, sha256, absolute: entry.absolute, destination, alreadyExists: Boolean(existing) });
    });
    const manifest = { version: 1, sourceGroup: group.id, status: 'source snapshot', files: files.map(({ path, source, bytes, sha256 }) => ({ path, source, bytes, sha256 })), excluded };
    const manifestPath = path.join(target, 'import-manifest.json');
    const expectedManifest = JSON.stringify(manifest, null, 2) + '\n';
    const existingManifest = await fs.readFile(manifestPath, 'utf8').catch(error => { if (error.code === 'ENOENT') return null; throw error; });
    if (apply && existingManifest && existingManifest !== expectedManifest) {
      if (!refreshManifest) throw new Error(`Refusing to replace changed manifest: ${group.target}; inspect dry-run and use --refresh-manifest to add files safely`);
      const previous = JSON.parse(existingManifest);
      const next = new Map(manifest.files.map(file => [file.path, file]));
      if (previous.sourceGroup !== manifest.sourceGroup || previous.files.some(file => next.get(file.path)?.sha256 !== file.sha256)) throw new Error(`Manifest refresh would remove or change prior imported files: ${group.target}`);
    }
    plans.push({ group, target, files, excluded, manifestPath, expectedManifest, existingManifest });
  }
  // All collision checks complete before any mutation.
  const summary = [];
  for (const { group, target, files, excluded, manifestPath, expectedManifest, existingManifest } of plans) {
    const item = { id: group.id, target: group.target, files: files.length, bytes: files.reduce((sum, file) => sum + file.bytes, 0), skipped: excluded.length, suspectedCredentials: excluded.filter(file => file.reason.startsWith('suspected')).map(file => file.path) };
    summary.push(item);
    if (!apply || !files.length) continue;
    await fs.mkdir(target, { recursive: true });
    for (const file of files) if (!file.alreadyExists) {
      await fs.mkdir(path.dirname(file.destination), { recursive: true });
      const buffer = await fs.readFile(file.absolute);
      if (digest(buffer) !== file.sha256) throw new Error(`Source changed after inspection: ${group.id}/${file.source}`);
      await fs.writeFile(file.destination, buffer, { flag: 'wx' });
    }
    if (!existingManifest) await fs.writeFile(manifestPath, expectedManifest, { flag: 'wx' });
    else if (existingManifest !== expectedManifest) await fs.writeFile(manifestPath, expectedManifest);
    const readmePath = path.join(target, 'README.md');
    if (!(await fs.stat(readmePath).catch(() => null))) {
      const readme = `# ${group.title}\n\n${group.description}\n\n本目录为选择性恢复的源码快照，运行与构建说明见下方资料。原课程已有笔记和实现继续保留。\n\n${group.requirements}\n\n只导入白名单文件。依赖、编译输出、服务器安装包、原始私人连接配置与疑似秘密文件均不复制；具体排除项与每个导入文件的 SHA256 见 [导入清单](./import-manifest.json)。\n\n从仓库根目录运行 \`node tools/import-local-labs.mjs --verify\` 可检查已保存文件完整性。以后重新导入默认 dry-run；脚本拒绝覆盖内容不同的既有文件。\n`;
      await fs.writeFile(readmePath, readme, { flag: 'wx' });
    }
  }
  console.log(JSON.stringify({ mode: apply ? 'apply' : 'dry-run', groups: summary, totalFiles: summary.reduce((sum, item) => sum + item.files, 0), totalBytes: summary.reduce((sum, item) => sum + item.bytes, 0) }, null, 2));
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
