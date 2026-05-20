# 批量重命名工具

一个用 Python 写的小工具，能批量给文件夹里的文件加前缀、加后缀、重命名成"统一名字 + 序号"，或者**查找替换文件名/文件夹名中的指定字段**。

只用了 Python 标准库（`tkinter`），**不需要 `pip install` 任何东西**。

## 运行

```bash
python rename_tool.py
```

## 四种模式

| 模式            | 效果                                                                         |
| --------------- | ---------------------------------------------------------------------------- |
| 加前缀          | `photo.jpg` → `IMG_photo.jpg`                                                |
| 加后缀          | `photo.jpg` → `photo_final.jpg`（扩展名前面加）                               |
| 统一名称 + 序号 | 全部改成 `photo_01.jpg`、`photo_02.jpg` ...，序号位数和起始值可调             |
| 查找替换        | 把文件名和文件夹名中的某个字段替换成另一个，例如 `old_photo.jpg` → `new_photo.jpg` |

## 主要特性

- **预览先行**：点"生成预览"先看新旧名字对比，确认无误再点"执行重命名"
- **冲突检测**：自动检查目标文件名是否重复或已存在
- **可撤销**：执行后可以一键还原上一次操作
- **过滤扩展名**：例如只填 `jpg,png` 就只改图片
- **可选递归**：勾上"包含子文件夹"会处理整棵目录树
- **两阶段重命名**：内部先改临时名再改最终名，避免 a↔b 互相重命名时的冲突
- **文件夹名也能改**：查找替换模式可以同时修改目标文件夹本身的名字
- **大小写可选**：查找替换支持不区分大小写匹配

## 命令行模式（可选）

不想开 GUI 也行：

```bash
# 加前缀 —— 预览后按回车执行
python rename_tool.py --cli prefix ./文件夹 IMG_

# 加后缀（只对 jpg、png 生效）
python rename_tool.py --cli suffix ./文件夹 _终版 --ext jpg,png

# 统一名 + 序号：旅行_01.jpg, 旅行_02.jpg ...
python rename_tool.py --cli seq ./文件夹 旅行 --start 1 --pad 2 --sep _

# 查找替换：把文件名中的 "旧" 替换成 "新"
python rename_tool.py --cli replace ./文件夹 旧 --replace-with 新

# 查找替换 + 同时改文件夹名
python rename_tool.py --cli replace ./文件夹 旧项目 --replace-with 新项目 --rename-folder

# 查找替换 + 不区分大小写
python rename_tool.py --cli replace ./文件夹 OldName --replace-with NewName --ignore-case

# 递归处理子文件夹
python rename_tool.py --cli prefix ./文件夹 IMG_ --recursive

# 跳过确认直接执行（不等回车）
python rename_tool.py --cli prefix ./文件夹 IMG_ -y
```

## CLI 参数说明

| 参数              | 适用模式   | 说明                                       |
| ----------------- | ---------- | ------------------------------------------ |
| `--cli`           | 全部       | 选择模式：`prefix` / `suffix` / `seq` / `replace` |
| `folder`          | 全部       | 目标文件夹路径                             |
| `text`            | 全部       | 前缀/后缀/基础名/查找字符串               |
| `-y` / `--yes`    | 全部       | 跳过确认直接执行（不等回车）               |
| `--ext`           | 全部       | 逗号分隔的扩展名过滤                       |
| `--recursive`     | 全部       | 递归处理子文件夹                           |
| `--start`         | seq        | 起始序号（默认 1）                         |
| `--pad`           | seq        | 序号位数（默认 2）                         |
| `--sep`           | seq        | 基础名和序号之间的分隔符（默认 `_`）       |
| `--replace-with`  | replace    | 替换成的字符串（可为空=删除匹配内容）      |
| `--ignore-case`   | replace    | 不区分大小写匹配                           |
| `--rename-folder` | replace    | 同时修改目标文件夹本身的名字               |
