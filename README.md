# 批量重命名工具

一个用 Python 写的小工具，能批量给文件夹里的文件加前缀、加后缀，或者重命名成"统一名字 + 序号"（例如 `photo_01.jpg`、`photo_02.jpg` ...）。

只用了 Python 标准库（`tkinter`），**不需要 `pip install` 任何东西**。

## 运行

```bash
python rename_tool.py
```

## 三种模式

| 模式            | 效果                                                             |
| --------------- | ---------------------------------------------------------------- |
| 加前缀          | `photo.jpg` → `IMG_photo.jpg`                                    |
| 加后缀          | `photo.jpg` → `photo_final.jpg`（扩展名前面加）                   |
| 统一名称 + 序号 | 全部改成 `photo_01.jpg`、`photo_02.jpg` ...，序号位数和起始值可调 |

## 主要特性

- **预览先行**：点"生成预览"先看新旧名字对比，确认无误再点"执行重命名"
- **冲突检测**：自动检查目标文件名是否重复或已存在
- **可撤销**：执行后可以一键还原上一次操作
- **过滤扩展名**：例如只填 `jpg,png` 就只改图片
- **可选递归**：勾上"包含子文件夹"会处理整棵目录树
- **两阶段重命名**：内部先改临时名再改最终名，避免 a↔b 互相重命名时的冲突

## 命令行模式（可选）

不想开 GUI 也行：

```bash
# 预览（不会真的改）
python rename_tool.py --cli prefix ./folder IMG_

# 真正执行
python rename_tool.py --cli prefix ./folder IMG_ --apply

# 加后缀（只对 jpg、png 生效）
python rename_tool.py --cli suffix ./folder _final --ext jpg,png --apply

# 统一名 + 序号：photo_01.jpg, photo_02.jpg ...
python rename_tool.py --cli seq ./folder photo --start 1 --pad 2 --sep _ --apply

# 递归处理子文件夹
python rename_tool.py --cli prefix ./folder IMG_ --recursive --apply
```
