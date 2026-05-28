# INSIGHT — AI Daily Magazine

静态网站，每日 AI 摘要，按月归档，通过 GitHub Pages 发布。
地址：https://wangboroy.github.io/insight/

## 每日发布流程

运行 `/follow-builders` 后，**必须执行以下步骤**将内容发布到网站：

1. 将 follow-builders 生成的摘要文本写入临时文件，例如 `C:\Temp\digest.txt`
2. 运行发布脚本：
   ```
   python scripts/save_digest.py --file C:\Temp\digest.txt
   ```
3. 脚本自动完成：生成 Markdown → 构建 HTML → git commit → git push → 网站更新

**整个流程不需要用户手动操作 git。**

## 内容存储格式

```
content/
  YYYY/
    MM/
      YYYY-MM-DD.md   ← 每日一篇，frontmatter + Markdown 正文
```

Frontmatter 格式（由脚本自动生成）：
```yaml
---
title: YYYY年MM月DD日 AI 摘要
date: YYYY-MM-DD
tags: Anthropic, OpenAI, ...
---
```

## 构建说明

```bash
pip install markdown
python build.py        # 输出到 docs/，本地预览用
```

`docs/` 已 gitignore，由 GitHub Actions 在 CI 中自动构建和部署。

## 网站需求备忘

- 存放历史摘要，按月归档（content/YYYY/MM/）
- 标题格式：YYYY年MM月DD日 AI 摘要
- 深色科技风格（黑色背景 + 青色高亮）
- 日报，非周报
