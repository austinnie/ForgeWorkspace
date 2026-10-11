"""
预设: 虬曲古梅石刻
分类: stone_carving
风格: 文人刻石（石版画）—— 以刀代笔的浅刻水墨
"""

PRESET = {
    "name": "虬曲古梅石刻",
    "category": "stone_carving",
    "tags": ["stone_carving", "plum_blossom", "literati_stone"],
    "layers": {
        # ============================================================
        # 主体：树 + 花，刻在石上
        # ============================================================
        "subject": [
            "gnarled old plum tree carved into a dark grey stone slab, "
            "ink-black branches spreading across the stone, "
            "plum blossoms carved as flat dark silhouettes directly in the stone surface",

            "twisting plum trunk incised into weathered slate, "
            "dense plum blossoms in deep ink-black pigment rubbed into the carved grooves, "
            "shallow relief on a stone panel",

            "ancient plum tree with sparse blossoms, "
            "carved into a flat grey stone board, "
            "ink-black motif flush with the stone surface, cracks and fissures visible",
        ],

        # ============================================================
        # 场景：真实老石板，明确 no paper
        # ============================================================
        "scene": [
            "weathered dark grey stone slab, vertical hairline cracks, chipped edges, "
            "uneven surface, mineral staining, no paper",

            "aged stone tablet with brown-grey patina, "
            "deep fissures across the surface, weathered corners, broken edge",

            "rough slate slab, natural cracks, faded mineral deposits, "
            "flat stone working surface, irregular broken edge",

            "ancient stone panel, mottled grey surface, "
            "long vertical cracks, chipped irregular edge, no frame",

            "weathered dark slate with subtle color variation, "
            "stone grain visible, natural cracks, no paper mounting",

            "old stone board, uneven broken edge, "
            "surface marked by time, faint scratches and mineral staining",
        ],

        # ============================================================
        # 风格：核心是"刻在石上"，不是"画在纸上"
        # ============================================================
        "style": [
            # ---- 核心：石上刻 ----
            "carved directly into dark grey slate, motif flush with the stone surface, "
            "deeply incised lines, mineral pigment in the grooves, no paper, no paint",

            "stone panel with carved plum motif, "
            "ink-black pigment rubbed into the shallow grooves, "
            "flat grey stone background, natural cracks and chips",

            "scholar's stone slab painting, motif carved as shallow relief, "
            "stone surface dominant, cracks and fissures visible across the panel",

            # ---- 石版画传统 ----
            "literati composition transferred to stone, "
            "ink-black silhouette incised into a weathered slab, "
            "no paper, no scroll, unmounted stone panel",

            "Chinese stone engraving, calligraphic rhythm, "
            "dark pigment in shallow grooves, aged stone slab, flat background",

            # ---- 年代与风格 ----
            "Ming-Qing literati stone carving, rustic elegance, "
            "uneven line weight, ink-black motif on grey stone, weathered surface",

            "traditional Chinese stone engraving, "
            "ink-black on natural grey stone, quiet and austere",
        ],

        # ============================================================
        # 光影：平光，只让石面有质感
        # ============================================================
        "lighting": [
            "soft flat lighting, subtle shadow in the carved grooves only, "
            "motif remains flat and dark, no highlights on the ink-black areas",

            "even diffused light across the stone surface, "
            "gentle tonal variation on the slab, no dramatic shadows",

            "flat museum lighting, matte stone surface, "
            "carved areas read as dark silhouettes, no specular highlight",

            "overcast daylight, quiet grey atmosphere, "
            "stone texture visible, motif unaffected by light direction",

            "low soft light, stone grain visible, "
            "incised lines slightly shadowed, everything else flat",
        ],

        # ============================================================
        # 构图：竖幅石板书
        # ============================================================
        "composition": [
            "vertical stone panel composition, trunk rising diagonally from the bottom",
            "traditional hanging-scroll layout on stone, asymmetrical balance, "
            "calligraphy column on the side",
            "square stone slab composition, motif in the center, "
            "inscription on the upper side, ample empty stone around",
            "vertical stone board, sparse composition, "
            "plum branches on one side, inscription column on the other",
            "full stone slab composition, motif filling the upper two-thirds, "
            "inscription and seals in the lower area",
        ],

        # ============================================================
        # 画质
        # ============================================================
        "quality": [
            "masterpiece, best quality, literati aesthetic, "
            "authentic stone surface, ink-black motif, quiet dignity",
            "8k uhd, natural stone texture, shallow carving detail, "
            "no gloss, flat tonal values",
            "museum-quality stone panel, mineral staining, hairline cracks, "
            "traditional Chinese scholar's aesthetic",
        ],

        # ============================================================
        # 负向：压纸面、压水墨画、压拓片、压3D、压装裱
        # ============================================================
        "negative": [
            # 通用
            "color, bright colors, modern, digital art, smooth surface, plastic",
            "3d render, cgi, cartoon, anime, cute, pastel colors",

            # 压死纸面
            "paper texture, rice paper, xuan paper, silk, scroll, hanging scroll, mounting",
            "paper background, aged paper, foxing spots, paper creases, folded paper",
            "paper edge, torn paper, deckled edge",

            # 压死水墨画
            "ink wash painting, sumi-e, watercolor, painting on paper, brush painting",
            "calligraphy on paper, album leaf painting, literati painting on paper",
            "gradient wash, soft blending, ink bleeding on paper",

            # 压死装裱
            "framed, mounting, scroll borders, silk brocade, decorative border",
            "album leaf, folding screen, handscroll, kakemono",

            # 压死高浮雕 / 立体
            "high relief, deep carving, protruding sculpture, "
            "thick dimensional relief, strong cast shadow, ambient occlusion",
            "sculpture, statue, dimensional motif, volumetric",

            # 压死照片
            "photograph, realistic photo, 3d scan, photogrammetry, "
            "depth of field, lens blur, cinematic lighting",

            # 压死拓片
            "black and white rubbing, torn paper edge, framed rubbing",
        ],

        # ============================================================
        # 题词：行书刻石
        # ============================================================
        "inscription": [
            "vertical Chinese calligraphy in running script incised into the stone surface, "
            "ink-black brushwork carved into the slab, two small red seals below",

            "literati colophon in cursive script, carved into the stone surface, "
            "long vertical column, red seal at the end",
        ],
    },
}