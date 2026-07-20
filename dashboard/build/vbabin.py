"""
Build a valid vbaProject.bin (OLE Compound File) containing working VBA modules,
so the generated .xlsm actually runs macros on open.

Implements:
  - MS-OVBA (2.4.1) LZ compression for the 'dir' stream and module source streams
  - A minimal MS-CFB (Compound File Binary) writer with FAT + mini-FAT support

Validated by round-tripping with olefile.
"""
import struct


# --------------------------------------------------------------------------
# MS-OVBA compression (per [MS-OVBA] 2.4.1.3)
# --------------------------------------------------------------------------
def _compress_chunk(chunk):
    """Compress one <=4096 byte decompressed chunk -> token stream (no header)."""
    out = bytearray()
    src = 0
    while src < len(chunk):
        flag_pos = len(out)
        out.append(0)  # placeholder flag byte
        flag = 0
        for bit in range(8):
            if src >= len(chunk):
                break
            # try to find a match in the already-emitted window
            best_len = 0
            best_off = 0
            # compute bit split for current position
            diff = src
            bit_count = 0
            while (1 << bit_count) < diff:
                bit_count += 1
            bit_count = max(4, bit_count)
            length_mask = 0xFFFF >> bit_count
            max_len = length_mask + 3
            win_start = 0
            # search
            cand = src - 1
            while cand >= win_start:
                if chunk[cand] == chunk[src]:
                    # extend match
                    mlen = 0
                    while (src + mlen < len(chunk) and
                           chunk[cand + mlen] == chunk[src + mlen] and
                           mlen < max_len):
                        mlen += 1
                    if mlen > best_len:
                        best_len = mlen
                        best_off = src - cand
                cand -= 1
            if best_len >= 3:
                offset_val = (best_off - 1) << (16 - bit_count)
                length_val = best_len - 3
                token = offset_val | length_val
                out += struct.pack('<H', token)
                flag |= (1 << bit)
                src += best_len
            else:
                out.append(chunk[src])
                src += 1
        out[flag_pos] = flag
    return bytes(out)


def compress(data):
    """MS-OVBA CompressedContainer for the given decompressed bytes."""
    out = bytearray([0x01])  # signature byte
    pos = 0
    while pos < len(data):
        chunk = data[pos:pos + 4096]
        pos += 4096
        compressed = _compress_chunk(chunk)
        if len(compressed) <= 4096:
            # compressed chunk (flag=1). VBA source always compresses within range.
            size = len(compressed)
            header = (0x8000 | 0x3000 | ((size - 1) & 0x0FFF))
            out += struct.pack('<H', header)
            out += compressed
        else:
            # incompressible full chunk: raw mode, exactly 4096 bytes, size field 0xFFF
            raw = chunk + b'\x00' * (4096 - len(chunk))
            header = (0x3000 | 0x0FFF)
            out += struct.pack('<H', header)
            out += raw
    return bytes(out)


# --------------------------------------------------------------------------
# Minimal Compound File Binary (CFB) writer
# --------------------------------------------------------------------------
FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
DIFSECT = 0xFFFFFFFC
NOSTREAM = 0xFFFFFFFF

SECTOR = 512
MINI_SECTOR = 64
MINI_CUTOFF = 4096


class DirEntry:
    def __init__(self, name, etype, color=1):
        self.name = name
        self.etype = etype  # 1=storage,2=stream,5=root
        self.color = color
        self.left = NOSTREAM
        self.right = NOSTREAM
        self.child = NOSTREAM
        self.start = ENDOFCHAIN
        self.size = 0
        self.clsid = b'\x00' * 16


def _chain(fat, sectors, start_index):
    """Append a list of sector indices as a chain in fat."""
    for i in range(len(sectors) - 1):
        fat[sectors[i]] = sectors[i + 1]
    fat[sectors[-1]] = ENDOFCHAIN


def build_cfb(streams):
    """
    streams: list of (path_tuple, data_bytes). path_tuple like ('VBA','dir').
    Storages are inferred. Returns compound file bytes.
    Layout used: red-black tree simplified to a right-leaning sorted list per level
    (Excel/olefile accept unbalanced but valid ordering by (len(name), upper(name))).
    """
    # Build directory tree
    root = DirEntry('Root Entry', 5, color=0)
    entries = {(): root}
    # collect storages
    storages = set()
    for path, data in streams:
        for i in range(1, len(path)):
            storages.add(path[:i])
    for s in sorted(storages, key=lambda p: len(p)):
        entries[s] = DirEntry(s[-1], 1)
    for path, data in streams:
        e = DirEntry(path[-1], 2)
        e.size = len(data)
        entries[path] = e

    # children grouping
    def sort_key(name):
        return (len(name), name.upper())

    children = {}
    for path, e in entries.items():
        if path == ():
            continue
        parent = path[:-1]
        children.setdefault(parent, []).append(path)

    # assign dir index order: BFS
    order = [()]
    idx = 0
    all_paths = [()]
    # we need deterministic index assignment. Use: root=0, then all others sorted.
    others = [p for p in entries if p != ()]
    others.sort(key=lambda p: (len(p), tuple(sort_key(n) for n in p)))
    all_paths = [()] + others
    index_of = {p: i for i, p in enumerate(all_paths)}

    # build child sibling trees (simple: sorted, left-balanced binary tree)
    def build_tree(paths):
        paths = sorted(paths, key=lambda p: sort_key(p[-1]))
        def rec(lo, hi):
            if lo > hi:
                return NOSTREAM
            mid = (lo + hi) // 2
            node = paths[mid]
            entries[node].left = rec(lo, mid - 1)
            entries[node].right = rec(mid + 1, hi)
            return index_of[node]
        return rec(0, len(paths) - 1)

    for parent, kids in children.items():
        entries[parent].child = build_tree(kids)

    # ----- assemble stream data -----
    # separate mini vs regular
    mini_stream_data = bytearray()
    regular_blobs = []  # (path, data)
    mini_entries = []   # (path, start_mini, size)

    # root entry stores mini stream in regular FAT
    for path in all_paths:
        if path == ():
            continue
        e = entries[path]
        if e.etype != 2:
            continue
        data = dict(streams)[path]
        if len(data) < MINI_CUTOFF and len(data) > 0:
            start_mini = len(mini_stream_data) // MINI_SECTOR
            e.start = start_mini
            mini_stream_data += data
            if len(data) % MINI_SECTOR:
                mini_stream_data += b'\x00' * (MINI_SECTOR - (len(data) % MINI_SECTOR))
        elif len(data) == 0:
            e.start = ENDOFCHAIN
        else:
            regular_blobs.append((path, data))

    # ---- lay out sectors ----
    # We'll compute: directory sectors, mini-FAT sectors, mini-stream sectors (in FAT),
    # regular stream sectors, and FAT sectors. Then a header.
    # Build content sectors first, assign FAT afterward.

    fat = []  # list of next-pointers, index=sector number

    def add_sectors(nbytes_or_data, is_data=True):
        """Return list of sector indices allocated; append content to sector_content."""
        pass

    sector_content = []  # list of 512-byte blocks

    def alloc_data(data):
        # pad to sector multiple
        if len(data) % SECTOR:
            data = data + b'\x00' * (SECTOR - (len(data) % SECTOR))
        n = len(data) // SECTOR
        idxs = []
        for i in range(n):
            idxs.append(len(sector_content))
            sector_content.append(data[i * SECTOR:(i + 1) * SECTOR])
        return idxs

    # 1. mini stream (root entry chain) - regular sectors
    mini_stream_sectors = alloc_data(bytes(mini_stream_data)) if mini_stream_data else []
    root.start = mini_stream_sectors[0] if mini_stream_sectors else ENDOFCHAIN
    root.size = len(mini_stream_data)

    # 2. mini FAT
    n_mini_sectors = len(mini_stream_data) // MINI_SECTOR
    minifat = [FREESECT] * 0
    # chain each mini stream: we stored them contiguously per entry
    minifat = []
    # rebuild minifat by walking entries again
    minifat = [ENDOFCHAIN] * n_mini_sectors
    # for each mini entry set proper chain
    for path in all_paths:
        if path == ():
            continue
        e = entries[path]
        if e.etype == 2 and e.start != ENDOFCHAIN and e.size < MINI_CUTOFF and e.size > 0:
            nsec = (e.size + MINI_SECTOR - 1) // MINI_SECTOR
            for k in range(nsec - 1):
                minifat[e.start + k] = e.start + k + 1
            minifat[e.start + nsec - 1] = ENDOFCHAIN
    minifat_bytes = b''.join(struct.pack('<I', x) for x in minifat)
    minifat_sectors = alloc_data(minifat_bytes) if minifat_bytes else []

    # 3. regular streams
    for path, data in regular_blobs:
        idxs = alloc_data(data)
        entries[path].start = idxs[0]
        entries[path].size = len(data)
        _chain(_FatDict(fat), idxs, idxs[0])  # placeholder; real chain built later
        # store chain separately
        entries[path]._sectors = idxs

    # 4. directory stream
    dir_bytes = bytearray()
    for path in all_paths:
        e = entries[path]
        name_utf16 = e.name.encode('utf-16-le')
        name_utf16 = name_utf16[:62]
        name_len = len(name_utf16) + 2
        namebuf = name_utf16 + b'\x00' * (64 - len(name_utf16))
        entry = bytearray(128)
        entry[0:64] = namebuf
        struct.pack_into('<H', entry, 64, name_len)
        entry[66] = e.etype
        entry[67] = e.color
        struct.pack_into('<I', entry, 68, e.left)
        struct.pack_into('<I', entry, 72, e.right)
        struct.pack_into('<I', entry, 76, e.child)
        entry[80:96] = e.clsid
        # start sector + size
        struct.pack_into('<I', entry, 116, e.start if e.start is not None else ENDOFCHAIN)
        struct.pack_into('<Q', entry, 120, e.size)
        dir_bytes += entry
    # pad directory to sector multiple (entries per sector =4)
    if len(dir_bytes) % SECTOR:
        dir_bytes += b'\x00' * (SECTOR - (len(dir_bytes) % SECTOR))
    dir_sectors = alloc_data(bytes(dir_bytes))

    # ---- Now build the FAT ----
    total_content = len(sector_content)
    # We need FAT sectors too; number depends on total sectors including FAT itself.
    # iterate to converge
    n_fat = 1
    while True:
        total = total_content + n_fat
        needed = (total + 127) // 128  # entries per FAT sector =128
        if needed <= n_fat:
            break
        n_fat += 1

    fat_array = [FREESECT] * ((total_content + n_fat + 127) // 128 * 128)

    # chain mini stream sectors
    if mini_stream_sectors:
        _chain(_FatDict2(fat_array), mini_stream_sectors, mini_stream_sectors[0])
    # chain minifat sectors
    if minifat_sectors:
        _chain(_FatDict2(fat_array), minifat_sectors, minifat_sectors[0])
    # chain regular streams
    for path, data in regular_blobs:
        idxs = entries[path]._sectors
        _chain(_FatDict2(fat_array), idxs, idxs[0])
    # chain dir sectors
    _chain(_FatDict2(fat_array), dir_sectors, dir_sectors[0])
    # FAT sectors themselves are placed after content
    fat_sector_indices = list(range(total_content, total_content + n_fat))
    for fi in fat_sector_indices:
        fat_array[fi] = FATSECT

    # write FAT sector content
    fat_flat = fat_array[:total_content + n_fat]
    # pad fat to multiple of 128
    if len(fat_flat) % 128:
        fat_flat += [FREESECT] * (128 - (len(fat_flat) % 128))
    fat_bytes = b''.join(struct.pack('<I', x) for x in fat_flat)
    # append FAT sectors to content
    for i in range(n_fat):
        sector_content.append(fat_bytes[i * SECTOR:(i + 1) * SECTOR])

    # ---- header ----
    header = bytearray(512)
    header[0:8] = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
    header[24:26] = struct.pack('<H', 0x003E)  # minor
    header[26:28] = struct.pack('<H', 0x0003)  # major (v3, 512 sectors)
    header[28:30] = struct.pack('<H', 0xFFFE)  # byte order
    header[30:32] = struct.pack('<H', 0x0009)  # sector shift 512
    header[32:34] = struct.pack('<H', 0x0006)  # mini sector shift 64
    struct.pack_into('<I', header, 44, n_fat)  # num FAT sectors
    struct.pack_into('<I', header, 48, dir_sectors[0])  # first dir sector
    struct.pack_into('<I', header, 56, MINI_CUTOFF)  # mini cutoff
    struct.pack_into('<I', header, 60, minifat_sectors[0] if minifat_sectors else ENDOFCHAIN)
    struct.pack_into('<I', header, 64, len(minifat_sectors))  # num minifat sectors
    struct.pack_into('<I', header, 68, ENDOFCHAIN)  # first DIFAT
    struct.pack_into('<I', header, 72, 0)  # num DIFAT sectors
    # DIFAT (first 109 entries)
    difat = [FREESECT] * 109
    for i, fi in enumerate(fat_sector_indices):
        if i < 109:
            difat[i] = fi
    for i in range(109):
        struct.pack_into('<I', header, 76 + i * 4, difat[i])

    out = bytes(header) + b''.join(sector_content)
    return out


class _FatDict:
    def __init__(self, lst):
        self.lst = lst
    def __setitem__(self, k, v):
        pass  # no-op placeholder used above


class _FatDict2:
    """Adapter so _chain can write into a python list by index."""
    def __init__(self, lst):
        self.lst = lst
    def __setitem__(self, k, v):
        self.lst[k] = v
    def __getitem__(self, k):
        return self.lst[k]


# --------------------------------------------------------------------------
# VBA project assembly
# --------------------------------------------------------------------------
def build_vba_project(modules, project_name="RCPLDashboard"):
    """
    modules: list of dicts:
       {'name': 'Module1', 'type': 'standard'|'document'|'class',
        'code': '...', 'doc_sheet': None or codename}
    Returns vbaProject.bin bytes.
    """
    # --- dir stream (decompressed) ---
    def rec(id_, data=b''):
        return struct.pack('<HI', id_, len(data)) + data

    dir_ = bytearray()
    # PROJECTINFORMATION
    dir_ += rec(0x0001, struct.pack('<I', 0x00000097))  # SysKind (win32) -> actually PROJECTSYSKIND
    # Correct order per spec:
    dir_ = bytearray()
    dir_ += rec(0x0001, struct.pack('<I', 1))                 # PROJECTSYSKIND win32
    dir_ += rec(0x004A, struct.pack('<I', 3))                 # PROJECTCOMPATVERSION
    dir_ += rec(0x0002, struct.pack('<I', 0x0409))            # PROJECTLCID
    dir_ += rec(0x0014, struct.pack('<I', 0x0409))            # PROJECTLCIDINVOKE
    dir_ += rec(0x0003, struct.pack('<I', 1252))             # PROJECTCODEPAGE
    pn = project_name.encode('latin-1')
    dir_ += rec(0x0004, pn)                                   # PROJECTNAME
    dir_ += rec(0x0005, b'')                                  # PROJECTDOCSTRING
    dir_ += struct.pack('<HI', 0x0040, 0)                     # docstring unicode reserved
    dir_ += rec(0x0006, b'')                                  # PROJECTHELPFILEPATH
    dir_ += struct.pack('<HI', 0x003D, 0)
    dir_ += rec(0x0007, struct.pack('<I', 0))                 # PROJECTHELPCONTEXT
    dir_ += rec(0x0008, struct.pack('<I', 0))                 # PROJECTLIBFLAGS
    dir_ += rec(0x0009, struct.pack('<IHH', 0x00030000, 0, 0))  # PROJECTVERSION (special: size fixed 4)
    # PROJECTVERSION has reserved size=4 then major(4)+minor(2)
    dir_ = _rebuild_dir(project_name, modules)
    dir_compressed = compress(dir_)

    # --- _VBA_PROJECT stream (performance cache; a minimal valid stub) ---
    vba_project = struct.pack('<HBBH', 0x61CC, 0xFF, 0x00, 0x0000)  # reserved + version + reserved
    # Minimal: Excel rebuilds this. Provide the required 7-byte header + a couple bytes.
    vba_project = b'\xcc\x61' + b'\xff\xff' + b'\x00\x00' + b'\x00'

    # --- module source streams (compressed) ---
    module_streams = {}
    for m in modules:
        header_text = ''
        source = m['code']
        text = source
        module_streams[m['name']] = compress(text.encode('latin-1', 'replace'))

    # --- PROJECT stream (text) ---
    project_lines = []
    project_lines.append('ID="{%s}"' % '5DAB4E80-8C1D-4F2A-9B3E-1234567890AB')
    for m in modules:
        if m['type'] == 'document':
            project_lines.append('Document=%s/&H00000000' % m['name'])
        elif m['type'] == 'class':
            project_lines.append('Class=%s' % m['name'])
        else:
            project_lines.append('Module=%s' % m['name'])
    project_lines.append('Name="%s"' % project_name)
    project_lines.append('HelpContextID="0"')
    project_lines.append('VersionCompatible32="393222000"')
    project_lines.append('CMG="0000"')
    project_lines.append('DPB="0000"')
    project_lines.append('GC="0000"')
    project_lines.append('')
    project_lines.append('[Host Extender Info]')
    project_lines.append('&H00000001={3832D640-CF90-11CF-8E43-00A0C911005A};VBE;&H00000000')
    project_lines.append('')
    project_text = '\r\n'.join(project_lines).encode('latin-1')

    # --- PROJECTwm stream ---
    wm = bytearray()
    for m in modules:
        wm += m['name'].encode('latin-1') + b'\x00'
        wm += m['name'].encode('utf-16-le') + b'\x00\x00'
    wm += b'\x00\x00'
    project_wm = bytes(wm)

    # --- assemble CFB streams ---
    streams = []
    streams.append((('PROJECT',), project_text))
    streams.append((('PROJECTwm',), project_wm))
    streams.append((('VBA', '_VBA_PROJECT'), vba_project))
    streams.append((('VBA', 'dir'), dir_compressed))
    for m in modules:
        streams.append((('VBA', m['name']), module_streams[m['name']]))

    return build_cfb(streams)


def _rebuild_dir(project_name, modules):
    """Build the decompressed 'dir' stream bytes."""
    def rec(id_, data):
        return struct.pack('<HI', id_, len(data)) + data

    pn = project_name.encode('latin-1')
    b = bytearray()
    # PROJECTINFORMATION
    b += rec(0x0001, struct.pack('<I', 1))        # SysKind win32
    b += rec(0x004A, struct.pack('<I', 3))        # CompatVersion
    b += rec(0x0002, struct.pack('<I', 0x0409))   # Lcid
    b += rec(0x0014, struct.pack('<I', 0x0409))   # LcidInvoke
    b += struct.pack('<HIH', 0x0003, 2, 1252)     # CodePage (Size=2)
    b += rec(0x0004, pn)                          # Name
    # DocString: record 0x0005 (ansi) + 0x0040 reserved (unicode)
    b += struct.pack('<HI', 0x0005, 0)
    b += struct.pack('<HI', 0x0040, 0)
    # HelpFilePath: 0x0006 + 0x003D reserved
    b += struct.pack('<HI', 0x0006, 0)
    b += struct.pack('<HI', 0x003D, 0)
    b += rec(0x0007, struct.pack('<I', 0))        # HelpContext
    b += rec(0x0008, struct.pack('<I', 0))        # LibFlags
    # Version: id 0x0009, reserved size 4, VersionMajor(4), VersionMinor(2)
    b += struct.pack('<HI', 0x0009, 4)
    b += struct.pack('<I', 1)                     # major
    b += struct.pack('<H', 0)                     # minor
    # Constants: 0x000C + 0x003C reserved
    b += struct.pack('<HI', 0x000C, 0)
    b += struct.pack('<HI', 0x003C, 0)
    # PROJECTREFERENCES: one reference to stdole/VBA. Minimal: skip references
    # (Excel tolerates missing refs for pure-VBA project; add the mandatory VBA ref)
    # NAME record for a reference
    def ref_name(name):
        out = bytearray()
        out += struct.pack('<HI', 0x0016, len(name))
        out += name.encode('latin-1')
        out += struct.pack('<HI', 0x003E, len(name) * 2)
        out += name.encode('utf-16-le')
        return out
    def ref_registered(libid):
        out = bytearray()
        out += struct.pack('<H', 0x000D)
        payload = struct.pack('<I', len(libid)) + libid.encode('latin-1')
        payload += struct.pack('<I', 0) + struct.pack('<H', 0)
        out += struct.pack('<I', len(payload)) + payload
        return out
    b += ref_name('stdole')
    b += ref_registered('*\\G{00020430-0000-0000-C000-000000000046}#2.0#0#C:\\Windows\\System32\\stdole2.tlb#OLE Automation')

    # PROJECTMODULES
    b += rec(0x000F, struct.pack('<H', len(modules)))
    b += struct.pack('<HI', 0x0013, 2) + struct.pack('<H', 0xFFFF)  # ProjectCookie
    offset_base = 0
    for m in modules:
        name = m['name']
        b += struct.pack('<HI', 0x0019, len(name)) + name.encode('latin-1')       # MODULENAME
        b += struct.pack('<HI', 0x0047, len(name) * 2) + name.encode('utf-16-le')  # MODULENAMEUNICODE
        b += struct.pack('<HI', 0x001A, len(name)) + name.encode('latin-1')       # MODULESTREAMNAME
        b += struct.pack('<HI', 0x0032, len(name) * 2) + name.encode('utf-16-le')
        b += struct.pack('<HI', 0x001C, 0)   # DocString
        b += struct.pack('<HI', 0x0048, 0)
        b += struct.pack('<HII', 0x0031, 4, 0)  # MODULEOFFSET (text offset in compressed source =0)
        b += struct.pack('<HII', 0x001E, 4, 0)  # HelpContext
        b += struct.pack('<HIH', 0x002C, 2, 0xFFFF)  # Cookie
        if m['type'] in ('document', 'class'):
            b += struct.pack('<HI', 0x0022, 0)  # MODULETYPE document/class (0x0022)
        else:
            b += struct.pack('<HI', 0x0021, 0)  # MODULETYPE procedural (0x0021)
        b += struct.pack('<HI', 0x002B, 0)      # MODULE terminator
    b += struct.pack('<HI', 0x0010, 0)          # PROJECTMODULES terminator / Terminator
    return bytes(b)


if __name__ == '__main__':
    import olefile
    mods = [
        {'name': 'ThisWorkbook', 'type': 'document', 'code':
            'Attribute VB_Name = "ThisWorkbook"\r\nOption Explicit\r\n'},
        {'name': 'modDashboard', 'type': 'standard', 'code':
            'Attribute VB_Name = "modDashboard"\r\nOption Explicit\r\n\r\n'
            'Sub Hello()\r\n    MsgBox "RCPL EHS Dashboard"\r\nEnd Sub\r\n'},
    ]
    data = build_vba_project(mods)
    with open('test_vba.bin', 'wb') as f:
        f.write(data)
    print("wrote", len(data), "bytes")
    ole = olefile.OleFileIO('test_vba.bin')
    print("streams:", ole.listdir())
    # decompress dir and a module to verify
    raw = ole.openstream('VBA/dir').read()
    from vbabin import compress
    # decompress
    def decompress(comp):
        out = bytearray()
        assert comp[0] == 0x01
        i = 1
        while i < len(comp):
            header = struct.unpack('<H', comp[i:i+2])[0]
            i += 2
            size = (header & 0x0FFF) + 1
            compressed = (header & 0x8000) != 0
            chunk = comp[i:i+size]
            i += size
            if not compressed:
                out += chunk[:4096]
                continue
            j = 0
            while j < len(chunk):
                flag = chunk[j]; j += 1
                for bit in range(8):
                    if j >= len(chunk):
                        break
                    if flag & (1 << bit):
                        token = struct.unpack('<H', chunk[j:j+2])[0]; j += 2
                        pos = len(out) - (len(out) % 4096) if len(out) % 4096 else len(out)
                        decomp_pos = len(out)
                        diff = decomp_pos - (decomp_pos - (decomp_pos % 4096)) if decomp_pos % 4096 else 0
                        # bit count based on position within chunk
                        cur = decomp_pos % 4096
                        bit_count = 4
                        while (1 << bit_count) < cur:
                            bit_count += 1
                        length_mask = 0xFFFF >> bit_count
                        length = (token & length_mask) + 3
                        offset = (token >> (16 - bit_count)) + 1
                        start = len(out) - offset
                        for k in range(length):
                            out.append(out[start + k])
                    else:
                        out.append(chunk[j]); j += 1
        return bytes(out)
    d = decompress(raw)
    print("dir decompressed len", len(d))
    src = decompress(ole.openstream('VBA/modDashboard').read())
    print("module source:\n", src.decode('latin-1'))
    ole.close()
