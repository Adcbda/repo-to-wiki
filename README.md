# code-to-wiki-claude

这是一个用于配合 Claude Code 生成项目 Wiki 的工作区模板。它把仓库分析、目录规划、内容生成、证据引用和质量校验拆成一套可复用的提示词与 skill 流程，目标是从本地源码仓库生成结构化、可追溯的 DeepWiki 风格文档。

## 项目组成

- `skills/generate-repo-wiki/`：Claude Code 使用的 Wiki 生成 skill，包含运行准备脚本、结构校验、证据校验和链接校验脚本。
- `catalogs-prompts/`：用于仓库分类、Wiki 目录结构规划和目录约束的提示词。
- `contents-prompts/`：用于证据选择、页面内容生成、图表生成和页面审阅的提示词。
- `myrepo/`：放置待分析源码仓库的目录。
- `wiki-generation/`：放置生成后的 Wiki 结果。
- `.wiki-run/`：生成过程中的中间状态、元数据、证据包和临时输出目录。

## 使用流程

1. 在项目根目录创建 `myrepo` 目录：

   ```powershell
   mkdir myrepo
   ```

2. 进入 `myrepo` 目录，并 clone 需要生成 Wiki 的代码仓库：

   ```powershell
   cd myrepo
   git clone <repo-url>
   ```

   clone 完成后，目录结构通常类似：

   ```text
   code-to-wiki-claude/
     myrepo/
       <仓库名称>/
   ```

3. 回到本项目根目录：

   ```powershell
   cd ..
   ```

4. 在 Claude Code 中，确保当前工作目录是本项目根目录，然后输入：

   ```text
   使用 wiki-generation 生成 myrepo/<仓库名称> 的 wiki
   ```

5. Claude Code 会读取 `myrepo/<仓库名称>` 中的源码，结合本项目内的提示词和 skill 流程生成 Wiki。生成结果会输出到 `wiki-generation/<仓库名称>/`，运行过程中的中间文件会放在 `.wiki-run/<仓库名称>/`。

## 示例

如果要为 `express` 仓库生成 Wiki：

```powershell
mkdir myrepo
cd myrepo
git clone https://github.com/expressjs/express.git
cd ..
```

然后在 Claude Code 中输入：

```text
使用 wiki-generation 生成 myrepo/express 的 wiki
```
