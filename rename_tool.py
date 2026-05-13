"""
批量重命名工具 (Batch Rename Tool)

功能：
  1. 加前缀：在文件名前面加上指定字符串
  2. 加后缀：在文件名后面（扩展名前）加上指定字符串
  3. 统一命名 + 序号：例如 photo_01.jpg、photo_02.jpg ...

特性：
  - 支持预览，先看效果再执行
  - 支持按扩展名过滤（如只处理 .jpg）
  - 支持是否包含子文件夹
  - 序号位数可调（01 / 001 / 0001 ...）
  - 序号起始值可调
  - 一键撤销上一次操作

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


def validate_plans(plans: list[RenamePlan]) -> list[str]:
    """返回错误列表（空列表表示全部通过）。"""
    errors: list[str] = []
    seen_targets: dict[Path, Path] = {}

    for plan in plans:
        if not plan.changed:
            continue

        # 1) 目标路径不能与已有的别的文件冲突
        if plan.dst.exists() and plan.dst != plan.src:
            errors.append(f"目标已存在：{plan.dst.name}（来源 {plan.src.name}）")

        # 2) 多个源不能改成同一个目标
        if plan.dst in seen_targets:
            errors.append(
                f"目标重名：{plan.dst.name} 同时来自 "
                f"{seen_targets[plan.dst].name} 和 {plan.src.name}"
            )
        else:
            seen_targets[plan.dst] = plan.src

        # 3) 文件名不能包含路径分隔符或非法字符
        if any(c in plan.dst.name for c in ('/', '\\', ':', '*', '?', '"', '<', '>', '|')):
            errors.append(f"非法文件名：{plan.dst.name}")

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
    """简单的命令行模式，方便没有 GUI 环境时也能用。

    用法示例：
      python rename_tool.py --cli prefix  ./folder  IMG_
      python rename_tool.py --cli suffix  ./folder  _final
      python rename_tool.py --cli seq     ./folder  photo  --start 1 --pad 2 --sep _
    可选参数：
      --ext jpg,png         仅处理这些扩展名
      --recursive           递归处理子文件夹
      --apply               不加则只预览，加上才会真的重命名
    """
    import argparse

    parser = argparse.ArgumentParser(description="批量重命名工具 (CLI 模式)")
    parser.add_argument("--cli", required=True, choices=["prefix", "suffix", "seq"])
    parser.add_argument("folder", type=Path)
    parser.add_argument("text", help="prefix/suffix 的字符串，或 seq 的基础名")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--pad", type=int, default=2)
    parser.add_argument("--sep", default="_", help="seq 模式下基础名和序号之间的分隔符")
    parser.add_argument("--ext", default="", help="逗号分隔的扩展名过滤，如 jpg,png")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--apply", action="store_true", help="真正执行；不加则只预览")
    args = parser.parse_args()

    exts = [e for e in args.ext.split(",") if e.strip()] or None
    files = collect_files(args.folder, recursive=args.recursive, extensions=exts)
    if not files:
        print("未找到匹配的文件。")
        return 1

    if args.cli == "prefix":
        plans = build_prefix_plans(files, args.text)
    elif args.cli == "suffix":
        plans = build_suffix_plans(files, args.text)
    else:
        plans = build_sequence_plans(
            files, args.text, start=args.start, pad=args.pad, separator=args.sep
        )

    errors = validate_plans(plans)
    print(f"共 {len(plans)} 个文件，将重命名 {sum(1 for p in plans if p.changed)} 个：")
    for p in plans:
        flag = " " if not p.changed else "*"
        print(f"  {flag} {p.src.name}  ->  {p.dst.name}")
    if errors:
        print("\n发现以下问题，未执行：")
        for e in errors:
            print(f"  - {e}")
        return 2

    if not args.apply:
        print("\n预览结束。加上 --apply 才会真正重命名。")
        return 0

    done = execute_plans(plans)
    print(f"\n完成，成功重命名 {len(done)} 个文件。")
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
            return ["prefix", "suffix", "seq"][idx]

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
            # seq
            base = self.var_base.get()
            if not base:
                messagebox.showwarning("提示", "请输入基础名。")
                return []
            return build_sequence_plans(
                files,
                base_name=base,
                start=int(self.var_start.get()),
                pad=int(self.var_pad.get()),
                separator=self.var_sep.get(),
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
