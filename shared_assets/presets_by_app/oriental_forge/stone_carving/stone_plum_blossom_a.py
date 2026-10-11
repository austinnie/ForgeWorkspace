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
        # 主体：树 + 花 + 竹叶式的点染
        # ============================================================
        "subject": [
            "gnarled old plum tree, ink-black branches spreading across a stone slab, "
            "plum blossoms carved as dark ink silhouettes, "
            "scholar's painting translated into shallow stone carving",

            "twisting plum trunk with rugged texture, "
            "dense plum blossoms in deep ink-black, carved on a flat stone surface, "
            "literati painting incised into stone",

            "ancient plum tree with sparse blossoms, "
            "ink-painted branches and flowers carved into a weathered stone tablet, "
            "traditional Chinese scholar's stone painting",
        ],

        # ============================================================
        # 场景：真实老石板
        # ============================================================
        "scene": [
            "worn dark grey stone slab, natural cracks and chips, "
            "uneven surface with mineral staining, edges broken by time",

            "aged stone tablet with brown-grey patina, "
            "hairline cracks across the surface, weathered corners",

            "rough slate slab, natural fissures, faded mineral deposits, "
            "flat working surface for carving",

            "ancient stone panel, mottled grey-brown surface, "
            "vertical hairline cracks, chipped edges",

            "weathered dark slate with subtle color variation, "
            "flat enough for carving, natural stone grain visible",

            "old stone tablet, uneven edge, "
            "surface marked by time, faint scratches and staining",
        ],

        # ============================================================
        # 风格：文人刻石核心
        # ============================================================
        "style": [
            # ---- 核心：石上水墨 ----
            "literati painting carved into stone, ink-black motif on grey stone slab, "
            "calligraphic brushwork translated into shallow incised lines",

            "Chinese scholar's stone painting, ink-wash composition incised into slate, "
            "dark motif on mottled grey stone, no shading, pure contour",

            "painted on stone, deep ink-black branches and blossoms carved shallowly "
            "into a weathered grey slab, uncolored, no fill",

            # ---- 浅刻技法 ----
            "shallow relief carving, motif barely raised from the flat stone, "
            "ink-black color applied to the carved areas",

            "incised line carving, hairline cuts, dark pigment rubbed into the grooves, "
            "flat stone background",

            "flat silhouette carved into stone, solid dark shapes, "
            "no modeling, no gradient, no lighting on the motif",

            # ---- 年代与风格 ----
            "Ming-Qing literati stone carving, rustic elegance, uneven line weight, "
            "ink-black motif on grey stone, weathered surface",

            "traditional Chinese stone engraving, calligraphic rhythm, "
            "dark pigment in shallow grooves, aged stone slab",

            "scholar's studio stone panel, plum blossom motif, "
            "ink-black on natural grey stone, quiet and austere",
        ],

        # ============================================================
        # 光影：平光，只让石面有质感，主体保持墨黑
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
        # 负向：压死 3D、照片、高浮雕、彩色、拓片、纸面
        # ============================================================
        "negative": [
            # 通用
            "color, bright colors, modern, digital art, smooth surface, plastic",
            "3d render, cgi, cartoon, anime, cute, pastel colors",

            # 压死"高浮雕 / 立体"
            "high relief, deep carving, protruding sculpture, "
            "thick dimensional relief, strong cast shadow, ambient occlusion",
            "sculpture, statue, dimensional motif, volumetric, "
            "deep shadow under motif",

            # 压死"照片感 / 3D 扫描"
            "photograph, realistic photo, 3d scan, photogrammetry, "
            "depth of field, lens blur, cinematic lighting",

            # 压死"拓片"
            "paper texture, rice paper, ink rubbing sheet, "
            "black and white rubbing, torn paper edge, framed rubbing",

            # 压死"水彩 / 水墨插画"
            "watercolor, ink wash painting on paper, illustration, "
            "soft blending, gradient wash, brush stroke on paper",

            # 压死"彩色石雕"
            "polished marble, glossy stone, reflective surface, "
            "colorful stone, painted stone",
        ],

        # ============================================================
        # 题词：行书/草书，像画家题款
        # ============================================================
        "inscription": [
            "vertical Chinese calligraphy in running script on the side, "
            "ink-black brushwork carved into stone, two small red seals below",

            "literati colophon in cursive script, carved into the stone surface, "
            "long vertical column, red seal at the end",
        ],
    },
}