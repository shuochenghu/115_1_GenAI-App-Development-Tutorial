"""Notebook程式格標註（第9～13週修訂版共用）。

用到前面格子定義的變數／函式時，在格首寫出名稱與出處，例如：
    # 用到前面格子定義的變數／函式（請先執行那些格子）：
    #   chunks、questions ← 第2節資料格
「先備：data、A」這類內部代號改成看得懂的格名，例如「先備：第2節資料格、第5節A格」。
標註由程式分析實際用到的名稱產生；前面找不到定義時直接停止，避免教材留下會NameError的格子。
"""
import builtins
import re
import symtable

NOTE_TITLE = "# 用到前面格子定義的變數／函式（請先執行那些格子）："
SEPARATORS = r"[、，]"


def cell_names(source):
    """回傳（這格頂層定義的名稱, 這格用到但沒有自己定義的名稱）；函式內用到的全域名稱也算。"""
    top = symtable.symtable(source, "<cell>", "exec")
    defined = {s.get_name() for s in top.get_symbols()
               if s.is_assigned() or s.is_imported() or s.is_namespace()}
    used = set()

    def walk(table):
        for symbol in table.get_symbols():
            if symbol.is_referenced() and (table.get_type() == "module" or symbol.is_global()):
                used.add(symbol.get_name())
        for child in table.get_children():
            walk(child)

    walk(top)
    return defined, used - defined - set(dir(builtins))


def imported_names(source):
    """這格用import匯入的名稱（標註時另列成「模組：」一行）。"""
    top = symtable.symtable(source, "<cell>", "exec")
    return {s.get_name() for s in top.get_symbols() if s.is_imported()}


def _tag(cell, prefix):
    return cell["id"].removeprefix(prefix)


def cell_labels(cells, prefix, nouns):
    """每個程式格的標籤，例如「第5節A格」；節次取自前一個##或###標題的編號。"""
    labels, section = {}, ""
    for cell in cells:
        text = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            found = re.match(r"#{2,3} (\d+(?:-\d+)?)", text)
            section = found.group(1) if found else section
        else:
            labels[_tag(cell, prefix)] = f"第{section}節{nouns[_tag(cell, prefix)]}"
    return labels


def dependency_sources(cells, prefix):
    """每個程式格：{出處格: ([用到的變數／函式], [用到的模組])}。前面找不到定義就停止。"""
    owner, modules, result = {}, set(), {}
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        tag = _tag(cell, prefix)
        source = "".join(cell["source"])
        defined, free = cell_names(source)
        missing = sorted(name for name in free if name not in owner)
        assert not missing, f"{tag}用到前面沒有定義的名稱：{missing}"
        sources = {}
        for name in sorted(free, key=str.lower):
            names, mods = sources.setdefault(owner[name], ([], []))
            (mods if name in modules else names).append(name)
        result[tag] = sources
        imported = imported_names(source)
        for name in defined:
            owner[name] = tag
            if name in imported:
                modules.add(name)
            else:
                modules.discard(name)
    return result


def note_lines(sources, labels, order, glossary=None):
    """產生格首標註：先列變數／函式，再把匯入的模組另列一行。
    有glossary時每個名稱後面加短說明，例如「offline_evidence（4題各自找到的片段）」，不必往回翻。"""
    lines = [NOTE_TITLE + "\n"]
    for source in sorted(sources, key=order.index):
        names, mods = sources[source]
        if glossary is not None:
            missing = [name for name in names if name not in glossary]
            assert not missing, f"glossary缺少說明：{missing}"
            names = [f"{name}（{glossary[name]}）" for name in names]
        if names:
            lines.append(f"#   {'、'.join(names)} ← {labels[source]}\n")
        if mods:
            lines.append(f"#   模組：{'、'.join(mods)} ← {labels[source]}\n")
    return lines


def _header_end(lines):
    end = 0
    while end < len(lines) and lines[end].startswith("#"):
        end += 1
    return end


HEADING_WITH_PERIOD = re.compile(r"^(#{2,3}) (\d+)\. ", re.M)


def normalize_headings(cells):
    """「## 2. 標題」改成「## 2 標題」：Colab目錄會把「2.」當成清單編號而不顯示，改後與「4-1」寫法一致。"""
    for cell in cells:
        if cell["cell_type"] == "markdown":
            text = HEADING_WITH_PERIOD.sub(r"\1 \2 ", "".join(cell["source"]))
            cell["source"] = text.splitlines(keepends=True)
    return cells


def annotate_dependencies(cells, prefix, nouns, aliases=None, glossary=None, direct_prereq=False):
    """補齊requires（含間接需要的格子）、改寫先備為格名，並在格首列出用到的名稱與出處。
    另把主節標題的「N.」改成「N」，讓Colab目錄看得到節次（格首標註用的就是節次）。
    direct_prereq=True時，「先備」只寫直接需要的格子（間接的仍在requires裡），格首比較短。"""
    normalize_headings(cells)
    aliases = aliases or {}
    labels = cell_labels(cells, prefix, nouns)
    sources = dependency_sources(cells, prefix)
    order = [_tag(c, prefix) for c in cells if c["cell_type"] == "code"]
    needed = {}
    for cell in cells:
        if cell["cell_type"] != "code":
            continue
        tag = _tag(cell, prefix)
        listed = {aliases.get(t, t) for t in cell["metadata"]["teaching"]["requires"]}
        wanted = set(sources[tag]) | listed
        for other in list(wanted):
            wanted |= needed[other]
        requires = [t for t in order if t in wanted]
        needed[tag] = set(requires)
        cell["metadata"]["teaching"]["requires"] = requires
        shown = requires
        if direct_prereq:   # 直接用到名稱的格子，加上手動列出、且不是被它們間接帶到的格子
            direct = set(sources[tag])
            implied = set().union(*(needed[t] for t in direct))
            shown = [t for t in order if t in direct or (t in listed and t not in implied)]

        lines = "".join(cell["source"]).splitlines(keepends=True)
        end = _header_end(lines)
        position = next((i for i in range(end) if "先備：" in lines[i]), None)
        if position is not None:
            def rewrite(match):
                tokens = [t.strip() for t in re.split(SEPARATORS, match.group(1)) if t.strip()]
                kept = [t for t in tokens if aliases.get(t, t) not in labels and t != "無"]
                return "先備：" + ("、".join([labels[r] for r in shown] + kept) or "無")
            lines[position] = re.sub(r"先備：([^；\n]+)", rewrite, lines[position], count=1)
        elif requires:
            lines.insert(0, "# 先備：" + "、".join(labels[r] for r in shown) + "\n")
            end += 1
        if sources[tag]:
            lines[end:end] = note_lines(sources[tag], labels, order, glossary)
        cell["source"] = lines
    return cells


def check_dependency_notes(cells, prefix, nouns, aliases=None, direct_prereq=False):
    """驗證用：每個用到的名稱都標了出處；出處（含間接）都在requires；先備寫出全部需要的格子
    （direct_prereq時至少寫出直接需要的）；先備不留內部代號。"""
    aliases = aliases or {}
    labels = cell_labels(cells, prefix, nouns)
    raw_tags = set(labels) | set(aliases)
    owner, needed, checked = {}, {}, 0
    for cell in cells:
        if cell["cell_type"] == "markdown":
            assert not HEADING_WITH_PERIOD.search("".join(cell["source"])), (cell["id"], "標題編號不可用「N.」")
        if cell["cell_type"] != "code":
            continue
        tag = _tag(cell, prefix)
        text = "".join(cell["source"])
        lines = text.splitlines()
        requires = set(cell["metadata"]["teaching"]["requires"])
        defined, free = cell_names(text)
        notes = {}
        for line in lines[:_header_end(lines)]:
            if line.startswith("#   ") and " ← " in line:
                names, label = line[4:].split(" ← ", 1)
                names = re.sub(r"（[^）]*）", "", names.removeprefix("模組："))   # 去掉名稱後的短說明
                for name in names.split("、"):
                    notes[name] = label
        direct = set()
        for name in free:
            assert name in owner, (tag, name)
            assert notes.get(name) == labels[owner[name]], (tag, name, notes.get(name))
            direct.add(owner[name])
        closure = set(direct)
        for source in direct:
            closure |= needed[source]
        assert closure <= requires, (tag, sorted(closure - requires))
        needed[tag] = requires
        assert (NOTE_TITLE in text) == bool(free), tag
        header = "\n".join(lines[:_header_end(lines)])
        found = re.search(r"先備：([^；\n]+)", header)
        if requires:
            assert found, (tag, "缺先備")
        if found:
            tokens = [t.strip() for t in re.split(SEPARATORS, found.group(1))]
            assert not (set(tokens) & raw_tags), (tag, found.group(1))
            for required in (direct if direct_prereq else requires):
                assert labels[required] in found.group(1), (tag, required)
        for name in defined:
            owner[name] = tag
        checked += 1
    return checked
