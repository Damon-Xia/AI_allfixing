"""
批量重命名工具 (Batch Rename Tool)

功能：
  1. 加前缀：在文件名前面加上指定字符串
  2. 加后缀：在文件名后面（扩展名前）加上指定字符串
  3. 统一命名 + 序号：例如 photo_01.jpg、photo_02.jpg ...
  4. 查找替换：将文件名和文件夹名中的指定字段替换为另一个

特性：
  - 支持预览，先看效果再执行
  - 支持按扩展名过滤（如只处理 .jpg）
  - 支持是否包含子文件夹
  - 序号位数可调（01 / 001 / 0001 ...）
  - 序号起始值可调
  - 一键撤销上一次操作
  - 查找替换可同时修改文件夹名，支持大小写不敏感

依赖：仅需 Python 3.8+ 标准库（tkinter），无需 pip 安装任何包。
运行：python rename_tool.py
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


# ---------------------------- 核心重命名逻辑 ---------------------------- #

@dataclass
class RenamePlan:
    """单个文件的重命名计划：源路径 -> 目标路径"""
    src: Path
    dst: Path

    @property
    def changed(self) -> bool:
        return self.src != self.dst


def collect_files(
    folder: Path,
    recursive: bool = False,
    extensions: Iterable[str] | None = None,
) -> list[Path]:
    """收集目标文件夹中需要被重命名的文件。

    Args:
        folder: 目标文件夹
        recursive: 是否递归处理子文件夹
        extensions: 仅处理这些扩展名（带或不带 '.' 都行），None 表示全部
    """
    if not folder.is_dir():
        return []

    # 规范化扩展名（统一小写、统一加点）
    norm_exts: set[str] | None = None
    if extensions:
        norm_exts = set()
        for ext in extensions:
            ext = ext.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = "." + ext
            norm_exts.add(ext)
        if not norm_exts:
            norm_exts = None

    iterator = folder.rglob("*") if recursive else folder.iterdir()
    files: list[Path] = []
    for p in iterator:
        if not p.is_file():
            continue
        if norm_exts is not None and p.suffix.lower() not in norm_exts:
            continue
        files.append(p)

    # 排序：先按相对路径，再按文件名，保证序号顺序稳定
    files.sort(key=lambda x: (str(x.parent).lower(), x.name.lower()))
    return files


def build_prefix_plans(files: list[Path], prefix: str) -> list[RenamePlan]:
    return [RenamePlan(f, f.with_name(f"{prefix}{f.name}")) for f in files]


def build_suffix_plans(files: list[Path], suffix: str) -> list[RenamePlan]:
    plans: list[RenamePlan] = []
    for f in files:
        stem, ext = f.stem, f.suffix
        new_name = f"{stem}{suffix}{ext}"
        plans.append(RenamePlan(f, f.with_name(new_name)))
    return plans


def build_sequence_plans(
    files: list[Path],
    base_name: str,
    start: int = 1,
    pad: int = 2,
    keep_ext: bool = True,
    separator: str = "",
) -> list[RenamePlan]:
    """统一命名 + 序号。例如 base='photo'、separator='_'、pad=2、start=1 -> photo_01.jpg"""
    plans: list[RenamePlan] = []
    for idx, f in enumerate(files, start=start):
        num = str(idx).zfill(pad)
        stem = f"{base_name}{separator}{num}" if base_name else num
        new_name = f"{stem}{f.suffix}" if keep_ext else stem
        plans.append(RenamePlan(f, f.with_name(new_name)))
    return plans


def build_replace_plans(
    files: list[Path],
    search: str,
    replace: str,
    case_sensitive: bool = True,
) -> list[RenamePlan]:
    """查找替换：将文件名中所有匹配 search 的子串替换为 replace。

    Args:
        files: 待处理的文件列表
        search: 要查找的字符串
        replace: 替换成的字符串
        case_sensitive: 是否区分大小写（默认区分）
    """
    import re as _re

    plans: list[RenamePlan] = []
    for f in files:
        name = f.name
        if case_sensitive:
            new_name = name.replace(search, replace)
        else:
            # 不区分大小写时用正则，用 lambda 避免 replace 中的反斜杠被当作正则转义
            new_name = _re.sub(_re.escape(search), lambda m: replace, name, flags=_re.IGNORECASE)
        plans.append(RenamePlan(f, f.with_name(new_name) if new_name else f))
    return plans


def replace_folder_name(
    folder: Path,
    search: str,
    replace: str,
    case_sensitive: bool = True,
) -> Path | None:
    """将目标文件夹本身的名字中的 search 替换为 replace。

    返回新的文件夹路径（如果有改动），None 表示不需要改或出错。
    注意：此操作会实际执行重命名（不是预览），调用前应先确认。
    """
    import re as _re

    old_name = folder.name
    if case_sensitive:
        new_name = old_name.replace(search, replace)
    else:
        new_name = _re.sub(_re.escape(search), lambda m: replace, old_name, flags=_re.IGNORECASE)

    if new_name == old_name:
        return None  # 无变化

    new_folder = folder.with_name(new_name)
    if new_folder.exists():
        raise OSError(f"目标文件夹已存在：{new_folder}")

    folder.rename(new_folder)
    return new_folder


def collect_files_by_ext(
    folder: Path,
    extensions: Iterable[str],
    recursive: bool = False,
) -> list[Path]:
    """按扩展名收集文件（用于删除场景）。

    Args:
        folder: 目标文件夹
        extensions: 要匹配的扩展名（带或不带 '.' 都可以），如 ['.meta', 'tmp']
        recursive: 是否递归处理子文件夹

    Returns:
        匹配到的文件列表（按路径排序），空列表表示没有匹配项。
    """
    if not folder.is_dir():
        return []

    # 规范化扩展名
    norm_exts: set[str] = set()
    for ext in extensions:
        ext = ext.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = "." + ext
        norm_exts.add(ext)
    if not norm_exts:
        return []

    iterator = folder.rglob("*") if recursive else folder.iterdir()
    files: list[Path] = []
    for p in iterator:
        if p.is_file() and p.suffix.lower() in norm_exts:
            files.append(p)
    files.sort(key=lambda x: (str(x.parent).lower(), x.name.lower()))
    return files


def delete_files(files: list[Path]) -> tuple[list[Path], list[tuple[Path, str]]]:
    """实际删除一组文件。

    Returns:
        (成功删除的文件列表, [(失败的文件, 错误信息), ...])
    注意：此操作不可撤销，调用前必须先让用户确认。
    """
    success: list[Path] = []
    failed: list[tuple[Path, str]] = []
    for f in files:
        try:
            f.unlink()
            success.append(f)
        except OSError as e:
            failed.append((f, str(e)))
    return success, failed


def validate_plans(plans: list[RenamePlan]) -> list[str]:
    """返回错误列表（空列表表示全部通过）。"""
    errors: list[str] = []
    seen_targets: dict[Path, Path] = {}

    for plan in plans:
        if not plan.changed:
            continue

        # 0) 文件名不能为空
        if not plan.dst.name or plan.dst.name.startswith('.') and not plan.dst.stem:
            errors.append(f"文件名为空或无效（来源：{plan.src.name}）")
            continue

        # 1) 目标路径不能与已有的别的文件冲突
        if plan.dst.exists() and plan.dst != plan.src:
            errors.append(f"目标文件已存在：{plan.dst.name}（来源：{plan.src.name}）")

        # 2) 多个源不能改成同一个目标
        if plan.dst in seen_targets:
            errors.append(
                f"目标名重复：{plan.dst.name}（来自 "
                f"{seen_targets[plan.dst].name} 和 {plan.src.name}）"
            )
        else:
            seen_targets[plan.dst] = plan.src

        # 3) 文件名不能包含路径分隔符或非法字符
        if any(c in plan.dst.name for c in ('/', '\\', ':', '*', '?', '"', '<', '>', '|')):
            errors.append(f"文件名含有非法字符：{plan.dst.name}")

    return errors


def execute_plans(
    plans: list[RenamePlan],
    on_progress: Callable[[int, int, RenamePlan], None] | None = None,
) -> list[RenamePlan]:
    """执行重命名，返回实际成功执行的计划列表（用于撤销）。

    采用两阶段重命名（先改成临时名，再改成目标名），避免循环重命名冲突，
    例如 a -> b、b -> a 同时发生时直接 rename 会冲突。
    """
    actionable = [p for p in plans if p.changed]
    total = len(actionable)
    done: list[RenamePlan] = []

    # 阶段 1：源 -> 临时名
    tmp_pairs: list[tuple[Path, Path]] = []
    for i, plan in enumerate(actionable, start=1):
        tmp = plan.src.with_name(f".__renaming__{os.getpid()}_{i}_{plan.src.name}")
        plan.src.rename(tmp)
        tmp_pairs.append((tmp, plan.dst))

    # 阶段 2：临时名 -> 目标名
    for i, (tmp, dst) in enumerate(tmp_pairs, start=1):
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp.rename(dst)
        plan = actionable[i - 1]
        done.append(plan)
        if on_progress:
            on_progress(i, total, plan)

    return done


# ---------------------------- 命令行入口（可选） ---------------------------- #

def run_cli() -> int:
    """命令行模式，方便没有图形界面的环境使用。

    用法示例：
      python rename_tool.py --cli prefix  ./文件夹  IMG_
      python rename_tool.py --cli suffix  ./文件夹  _终版
      python rename_tool.py --cli seq     ./文件夹  照片  --start 1 --pad 2 --sep _
      python rename_tool.py --cli replace ./文件夹  旧名  --replace-with 新名 --rename-folder
    可选参数：
      --ext jpg,png         仅处理这些扩展名
      --recursive           递归处理子文件夹
      -y                    跳过确认直接执行（不等待回车）
    """
    import argparse

    parser = argparse.ArgumentParser(description="批量重命名工具（命令行模式）")
    parser.add_argument("--cli", required=True, choices=["prefix", "suffix", "seq", "replace"],
                        help="模式：加前缀 / 加后缀 / 统一序号 / 查找替换")
    parser.add_argument("folder", type=Path, help="目标文件夹路径")
    parser.add_argument("text", help="前缀/后缀/基础名/查找字符串")
    parser.add_argument("--start", type=int, default=1, help="起始序号（默认 1）")
    parser.add_argument("--pad", type=int, default=2, help="序号位数（默认 2）")
    parser.add_argument("--sep", default="_", help="基础名和序号之间的分隔符（默认 _）")
    parser.add_argument("--replace-with", default="", help="替换为的字符串")
    parser.add_argument("--ignore-case", action="store_true", help="不区分大小写")
    parser.add_argument("--rename-folder", action="store_true", help="同时修改文件夹名")
    parser.add_argument("--delete-ext", default="",
                        help="（仅 replace 模式）同时删除这些扩展名的文件，逗号分隔，如 meta,tmp")
    parser.add_argument("--ext", default="", help="扩展名过滤，逗号分隔，如 jpg,png")
    parser.add_argument("--recursive", action="store_true", help="递归处理子文件夹")
    parser.add_argument("-y", "--yes", action="store_true", help="跳过确认直接执行")
    args = parser.parse_args()

    exts = [e for e in args.ext.split(",") if e.strip()] or None
    files = collect_files(args.folder, recursive=args.recursive, extensions=exts)

    # replace 模式可以单独触发删除：即使没有可改名的文件，只要要删的文件存在也应继续
    delete_exts = [e for e in args.delete_ext.split(",") if e.strip()] if args.cli == "replace" else []
    files_to_delete: list[Path] = []
    if delete_exts:
        files_to_delete = collect_files_by_ext(args.folder, delete_exts, recursive=args.recursive)

    if not files and not files_to_delete:
        print("未找到匹配的文件。")
        return 1

    if args.cli == "prefix":
        plans = build_prefix_plans(files, args.text)
    elif args.cli == "suffix":
        plans = build_suffix_plans(files, args.text)
    elif args.cli == "replace":
        plans = build_replace_plans(
            files, args.text, args.replace_with,
            case_sensitive=not args.ignore_case,
        )
    else:
        plans = build_sequence_plans(
            files, args.text, start=args.start, pad=args.pad, separator=args.sep
        )

    errors = validate_plans(plans)
    change_count = sum(1 for p in plans if p.changed)
    print(f"\n共 {len(plans)} 个文件，将重命名 {change_count} 个：\n")
    for p in plans:
        flag = "  " if not p.changed else "* "
        print(f"  {flag}{p.src.name}  →  {p.dst.name}")

    # 显示待删除的文件
    if files_to_delete:
        print(f"\n另外，将删除 {len(files_to_delete)} 个 {','.join(delete_exts)} 类型的文件：\n")
        for f in files_to_delete:
            print(f"  ✗ {f.name}")

    if errors:
        print("\n【发现以下问题，无法执行】")
        for e in errors:
            print(f"  ✗ {e}")
        return 2

    if change_count == 0 and not files_to_delete:
        print("\n没有需要改名或删除的文件。")
        return 0

    # 确认执行：按回车键执行，Ctrl+C 取消
    if not args.yes:
        try:
            if files_to_delete:
                input("\n按【回车键】执行重命名 + 删除，按 Ctrl+C 取消 ... ")
            else:
                input("\n按【回车键】执行重命名，按 Ctrl+C 取消 ... ")
        except (KeyboardInterrupt, EOFError):
            print("\n已取消。")
            return 0

    # 1) 先做重命名
    if change_count > 0:
        done = execute_plans(plans)
        print(f"\n✓ 完成！成功重命名 {len(done)} 个文件。")

    # 2) 删除指定扩展名文件
    if files_to_delete:
        deleted, failed = delete_files(files_to_delete)
        print(f"✓ 成功删除 {len(deleted)} 个文件。")
        if failed:
            print(f"✗ {len(failed)} 个文件删除失败：")
            for f, msg in failed:
                print(f"    - {f.name}：{msg}")

    # 查找替换模式可选：同时改文件夹名
    if args.cli == "replace" and args.rename_folder:
        try:
            new_folder = replace_folder_name(
                args.folder, args.text, args.replace_with,
                case_sensitive=not args.ignore_case,
            )
            if new_folder:
                print(f"✓ 文件夹已重命名：{args.folder.name}  →  {new_folder.name}")
            else:
                print("  文件夹名无需变更。")
        except OSError as e:
            print(f"✗ 文件夹重命名失败：{e}")
            return 3

    return 0


# ---------------------------- GUI ---------------------------- #

def run_gui() -> int:
    """启动 GUI 模式。"""
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    class RenameToolGUI:
        """GUI 主窗口。"""

        def __init__(self) -> None:
            self._root = tk.Tk()
            self._root.title("批量重命名工具")
            self._root.geometry("820x560")
            self._root.minsize(720, 480)

            self._plans: list[RenamePlan] = []
            self._last_done: list[RenamePlan] = []

            self._build_ui()

        def mainloop(self) -> None:
            self._root.mainloop()

        # ---------- UI 构建 ---------- #
        def _build_ui(self) -> None:
            pad = {"padx": 8, "pady": 4}
            root = self._root

            # 文件夹选择
            top = ttk.Frame(root)
            top.pack(fill="x", **pad)
            ttk.Label(top, text="文件夹：").pack(side="left")
            self.var_folder = tk.StringVar()
            ttk.Entry(top, textvariable=self.var_folder).pack(side="left", fill="x", expand=True, padx=4)
            ttk.Button(top, text="浏览...", command=self._choose_folder).pack(side="left")

            # 过滤选项
            opt = ttk.Frame(root)
            opt.pack(fill="x", **pad)
            ttk.Label(opt, text="扩展名过滤（逗号分隔，留空=全部）：").pack(side="left")
            self.var_ext = tk.StringVar()
            ttk.Entry(opt, textvariable=self.var_ext, width=20).pack(side="left", padx=4)
            self.var_recursive = tk.BooleanVar(value=False)
            ttk.Checkbutton(opt, text="包含子文件夹", variable=self.var_recursive).pack(side="left", padx=12)

            # 模式选择 Notebook
            nb = ttk.Notebook(root)
            nb.pack(fill="x", **pad)
            self.nb = nb

            # --- 加前缀 ---
            tab_prefix = ttk.Frame(nb)
            nb.add(tab_prefix, text="加前缀")
            ttk.Label(tab_prefix, text="前缀：").grid(row=0, column=0, sticky="w", **pad)
            self.var_prefix = tk.StringVar(value="IMG_")
            ttk.Entry(tab_prefix, textvariable=self.var_prefix, width=30).grid(row=0, column=1, sticky="w", **pad)
            ttk.Label(tab_prefix, text="例：IMG_ + photo.jpg = IMG_photo.jpg", foreground="gray").grid(
                row=1, column=0, columnspan=2, sticky="w", **pad
            )

            # --- 加后缀 ---
            tab_suffix = ttk.Frame(nb)
            nb.add(tab_suffix, text="加后缀")
            ttk.Label(tab_suffix, text="后缀：").grid(row=0, column=0, sticky="w", **pad)
            self.var_suffix = tk.StringVar(value="_final")
            ttk.Entry(tab_suffix, textvariable=self.var_suffix, width=30).grid(row=0, column=1, sticky="w", **pad)
            ttk.Label(tab_suffix, text="例：photo.jpg + _final = photo_final.jpg", foreground="gray").grid(
                row=1, column=0, columnspan=2, sticky="w", **pad
            )

            # --- 统一命名 + 序号 ---
            tab_seq = ttk.Frame(nb)
            nb.add(tab_seq, text="统一名称 + 序号")
            ttk.Label(tab_seq, text="基础名：").grid(row=0, column=0, sticky="w", **pad)
            self.var_base = tk.StringVar(value="photo")
            ttk.Entry(tab_seq, textvariable=self.var_base, width=20).grid(row=0, column=1, sticky="w", **pad)

            ttk.Label(tab_seq, text="分隔符：").grid(row=0, column=2, sticky="w", **pad)
            self.var_sep = tk.StringVar(value="_")
            ttk.Entry(tab_seq, textvariable=self.var_sep, width=6).grid(row=0, column=3, sticky="w", **pad)

            ttk.Label(tab_seq, text="起始序号：").grid(row=1, column=0, sticky="w", **pad)
            self.var_start = tk.IntVar(value=1)
            ttk.Spinbox(tab_seq, from_=0, to=999999, textvariable=self.var_start, width=8).grid(
                row=1, column=1, sticky="w", **pad
            )

            ttk.Label(tab_seq, text="序号位数：").grid(row=1, column=2, sticky="w", **pad)
            self.var_pad = tk.IntVar(value=2)
            ttk.Spinbox(tab_seq, from_=1, to=10, textvariable=self.var_pad, width=6).grid(
                row=1, column=3, sticky="w", **pad
            )

            ttk.Label(
                tab_seq, text="例：photo + _ + 01 = photo_01.jpg, photo_02.jpg ...", foreground="gray"
            ).grid(row=2, column=0, columnspan=4, sticky="w", **pad)

            # --- 查找替换 ---
            tab_replace = ttk.Frame(nb)
            nb.add(tab_replace, text="查找替换")
            ttk.Label(tab_replace, text="查找：").grid(row=0, column=0, sticky="w", **pad)
            self.var_search = tk.StringVar()
            ttk.Entry(tab_replace, textvariable=self.var_search, width=25).grid(row=0, column=1, sticky="w", **pad)

            ttk.Label(tab_replace, text="替换为：").grid(row=0, column=2, sticky="w", **pad)
            self.var_replace = tk.StringVar()
            ttk.Entry(tab_replace, textvariable=self.var_replace, width=25).grid(row=0, column=3, sticky="w", **pad)

            self.var_ignore_case = tk.BooleanVar(value=False)
            ttk.Checkbutton(tab_replace, text="不区分大小写", variable=self.var_ignore_case).grid(
                row=1, column=0, columnspan=2, sticky="w", **pad
            )
            self.var_rename_folder = tk.BooleanVar(value=True)
            ttk.Checkbutton(tab_replace, text="同时修改文件夹名", variable=self.var_rename_folder).grid(
                row=1, column=2, columnspan=2, sticky="w", **pad
            )

            # 同时删除指定扩展名的文件
            ttk.Label(tab_replace, text="同时删除这些扩展名的文件（逗号分隔，如 meta,tmp）：").grid(
                row=2, column=0, columnspan=2, sticky="w", **pad
            )
            self.var_delete_ext = tk.StringVar()
            ttk.Entry(tab_replace, textvariable=self.var_delete_ext, width=25).grid(
                row=2, column=2, columnspan=2, sticky="w", **pad
            )

            ttk.Label(
                tab_replace,
                text="例：查找 'old' 替换 'new'：old_photo.jpg → new_photo.jpg；并可勾选同时删除 .meta 文件",
                foreground="gray",
            ).grid(row=3, column=0, columnspan=4, sticky="w", **pad)

            # 操作按钮
            btns = ttk.Frame(root)
            btns.pack(fill="x", **pad)
            ttk.Button(btns, text="生成预览", command=self._preview).pack(side="left")
            ttk.Button(btns, text="执行重命名", command=self._apply).pack(side="left", padx=8)
            ttk.Button(btns, text="撤销上一次", command=self._undo).pack(side="left")
            self.lbl_status = ttk.Label(btns, text="就绪", foreground="gray")
            self.lbl_status.pack(side="right")

            # 预览表格
            table_frame = ttk.Frame(root)
            table_frame.pack(fill="both", expand=True, **pad)

            cols = ("idx", "old", "new", "status")
            self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
            self.tree.heading("idx", text="#")
            self.tree.heading("old", text="原文件名")
            self.tree.heading("new", text="新文件名")
            self.tree.heading("status", text="状态")
            self.tree.column("idx", width=50, anchor="center")
            self.tree.column("old", width=300)
            self.tree.column("new", width=300)
            self.tree.column("status", width=120, anchor="center")

            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=vsb.set)
            self.tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

        # ---------- 事件处理 ---------- #
        def _choose_folder(self) -> None:
            folder = filedialog.askdirectory(title="选择目标文件夹")
            if folder:
                self.var_folder.set(folder)

        def _current_mode(self) -> str:
            idx = self.nb.index(self.nb.select())
            return ["prefix", "suffix", "seq", "replace"][idx]

        def _build_plans(self) -> list[RenamePlan]:
            folder_str = self.var_folder.get().strip()
            if not folder_str:
                messagebox.showwarning("提示", "请先选择文件夹。")
                return []
            folder = Path(folder_str)
            if not folder.is_dir():
                messagebox.showerror("错误", f"文件夹不存在：{folder}")
                return []

            exts = [e for e in self.var_ext.get().split(",") if e.strip()] or None
            files = collect_files(folder, recursive=self.var_recursive.get(), extensions=exts)
            if not files:
                messagebox.showinfo("提示", "未找到匹配的文件。")
                return []

            mode = self._current_mode()
            if mode == "prefix":
                text = self.var_prefix.get()
                if not text:
                    messagebox.showwarning("提示", "请输入前缀。")
                    return []
                return build_prefix_plans(files, text)
            if mode == "suffix":
                text = self.var_suffix.get()
                if not text:
                    messagebox.showwarning("提示", "请输入后缀。")
                    return []
                return build_suffix_plans(files, text)
            if mode == "seq":
                base = self.var_base.get()
                if not base:
                    messagebox.showwarning("提示", "请输入基础名。")
                    return []
                try:
                    start_val = int(self.var_start.get())
                    pad_val = int(self.var_pad.get())
                except (ValueError, tk.TclError):
                    messagebox.showwarning("提示", "起始序号和位数必须是整数。")
                    return []
                return build_sequence_plans(
                    files,
                    base_name=base,
                    start=start_val,
                    pad=pad_val,
                    separator=self.var_sep.get(),
                )
            # replace
            search = self.var_search.get()
            if not search:
                messagebox.showwarning("提示", "请输入要查找的字符串。")
                return []
            return build_replace_plans(
                files, search, self.var_replace.get(),
                case_sensitive=not self.var_ignore_case.get(),
            )

        def _refresh_table(self, plans: list[RenamePlan], errors: list[str]) -> None:
            for item in self.tree.get_children():
                self.tree.delete(item)
            for i, p in enumerate(plans, start=1):
                if not p.changed:
                    status = "无变化"
                else:
                    status = "待执行"
                self.tree.insert("", "end", values=(i, p.src.name, p.dst.name, status))

            change_count = sum(1 for p in plans if p.changed)
            if errors:
                self.lbl_status.config(
                    text=f"预览 {len(plans)} 个文件，{change_count} 个待改 — 有冲突",
                    foreground="red",
                )
                messagebox.showwarning("发现问题", "\n".join(errors[:20]))
            else:
                self.lbl_status.config(
                    text=f"预览 {len(plans)} 个文件，{change_count} 个待改",
                    foreground="black",
                )

        def _preview(self) -> None:
            plans = self._build_plans()
            if not plans:
                return
            errors = validate_plans(plans)
            self._plans = plans
            self._refresh_table(plans, errors)

        def _apply(self) -> None:
            if not self._plans:
                self._preview()
                if not self._plans:
                    return

            errors = validate_plans(self._plans)
            if errors:
                messagebox.showerror("不能执行", "存在冲突，请先解决：\n" + "\n".join(errors[:20]))
                return

            change_count = sum(1 for p in self._plans if p.changed)
            if change_count == 0:
                messagebox.showinfo("提示", "没有任何需要改名的文件。")
                return

            if not messagebox.askyesno("确认", f"确定要重命名 {change_count} 个文件吗？"):
                return

            try:
                done = execute_plans(self._plans)
            except OSError as e:
                messagebox.showerror("失败", f"重命名时出错：{e}")
                return

            self._last_done = done
            self._plans = []
            self.lbl_status.config(
                text=f"已完成，重命名 {len(done)} 个文件。可点'撤销上一次'还原。",
                foreground="green",
            )

            for item in self.tree.get_children():
                self.tree.delete(item)
            for i, p in enumerate(done, start=1):
                self.tree.insert("", "end", values=(i, p.src.name, p.dst.name, "已完成"))

            # replace 模式：同时改文件夹名
            if self._current_mode() == "replace" and self.var_rename_folder.get():
                folder = Path(self.var_folder.get().strip())
                search = self.var_search.get()
                replace_str = self.var_replace.get()
                try:
                    new_folder = replace_folder_name(
                        folder, search, replace_str,
                        case_sensitive=not self.var_ignore_case.get(),
                    )
                    if new_folder:
                        self.var_folder.set(str(new_folder))
                        messagebox.showinfo(
                            "文件夹已改名",
                            f"{folder.name}  ->  {new_folder.name}",
                        )
                except OSError as e:
                    messagebox.showwarning("文件夹改名失败", str(e))

        def _undo(self) -> None:
            if not self._last_done:
                messagebox.showinfo("提示", "没有可以撤销的操作。")
                return
            if not messagebox.askyesno("确认", f"确定要撤销上一次重命名（{len(self._last_done)} 个文件）吗？"):
                return

            reverse_plans = [RenamePlan(p.dst, p.src) for p in self._last_done]
            errors = validate_plans(reverse_plans)
            if errors:
                messagebox.showerror("撤销失败", "撤销时检测到冲突：\n" + "\n".join(errors[:20]))
                return
            try:
                execute_plans(reverse_plans)
            except OSError as e:
                messagebox.showerror("撤销失败", str(e))
                return

            self._last_done = []
            self.lbl_status.config(text="已撤销上一次操作。", foreground="green")
            for item in self.tree.get_children():
                self.tree.delete(item)

    app = RenameToolGUI()
    app.mainloop()
    return 0


# ---------------------------- 入口 ---------------------------- #

if __name__ == "__main__":
    if "--cli" in sys.argv:
        sys.exit(run_cli())
    sys.exit(run_gui())
