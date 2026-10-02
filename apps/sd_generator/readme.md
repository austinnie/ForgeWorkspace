# 查看所有可用预设
python apps/sd_generator/cli.py --list-presets

# 查看本地可用模型
python apps/sd_generator/cli.py --list-models

# 查看支持的 API 引擎
python apps/sd_generator/cli.py --list-apis


# 1. 指定完整的三层路径（App分类 + 主题 + 预设名）
python apps/sd_generator/cli.py --app oriental_forge --theme region --preset dragon

# 2. 仅指定预设名（程序会自动在所有分类中全局搜索）
python apps/sd_generator/cli.py --preset dragon_sketch

# 3. 使用预设，但用自定义 prompt 覆盖预设的“主体(Subject)”层
python apps/sd_generator/cli.py --preset dragon_sketch --prompt "a cute cat sitting on a sofa"

# 使用完全免费的 freeapi（无需配置 Key）
python apps/sd_generator/cli.py --prompt "a cyberpunk city at night, neon lights" --api --api-provider freeapi

# 使用 Agnes AI（需在 .env 中配置 AGNES_API_KEY）
python apps/sd_generator/cli.py --prompt "a beautiful landscape" --api --api-provider agnes --steps 30

# 自动选择第一个 SD1.5 模型
python apps/sd_generator/cli.py --prompt "a warrior in armor"

# 指定具体的本地模型名称（通过 --list-models 查看）
python apps/sd_generator/cli.py --model aiiiiii01_v10 --prompt "a warrior in armor" --steps 25 --cfg 7.5





## ⚙️ 完整参数说明

运行 `python apps/sd_generator/cli.py --help` 可查看完整帮助。

### 查询命令
| 参数 | 说明 |
| :--- | :--- |
| `--list-presets` | 列出所有预设分类和名称 |
| `--list-models` | 列出本地可用模型 (SD1.5/SDXL) |
| `--list-apis` | 列出支持的 API 引擎及 Key 配置状态 |

### 预设与提示词
| 参数 | 说明 |
| :--- | :--- |
| `--app` | App 分类目录名 (如 `oriental_forge`, `sketch_forge`) |
| `--theme` | 主题分类目录名 (如 `region`, `musician`) |
| `--preset` | 预设名称 (不含 `.py`，如 `dragon`) |
| `--prompt` | 正向提示词 (会覆盖预设的 `subject` 层) |
| `--negative` | 负面提示词 |

### 引擎与模型
| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `--api` | 启用 API 引擎模式 (不加则默认使用本地模型) | `False` |
| `--api-provider` | API 提供商 (`freeapi`, `pollinations`, `agnes`, `siliconflow` 等) | `freeapi` |
| `--model` | 本地模型名称 | 自动选择第一个 SD1.5 |

### 生成参数
| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `--steps` | 采样步数 | `20` |
| `--cfg` | CFG Scale (提示词相关性) | `7.5` |
| `--width` | 图片宽度 | `512` (SDXL 会自动调整为 1024) |
| `--height` | 图片高度 | `768` (SDXL 会自动调整为 1024) |
| `--seed` | 随机种子 | 随机 |
| `--output` | 自定义输出目录 | `apps/sd_generator/output/` |

---

## 📂 目录结构

经过“薄壳化”重构，`sd_generator` 的目录极其精简：

```text
apps/sd_generator/
│
├── cli.py              # 唯一的入口文件 (纯壳，调用 forgecore)
└── output/             # 图片输出目录 (自动生成)







E:\SD_OpenVINO\ForgeWorkspace>python apps/sd_generator/cli.py --list-presets
SegDetector/UniformerDetector 不可用，请更新 controlnet-aux

======================================================================
📚 预设库 (shared_assets/presets_by_app/)
======================================================================

📁 [3d_render_forge]
----------------------------------------------------------------------
  📂 general/ (21 个)
    jewelry_showcase        mecha                   mecha_3d_prototype_dynamic    mecha_blueprint         mecha_chinese_warrior
    mecha_dark_queen        mecha_girl_doll_kit     mecha_girl_doll_series    mecha_girl_warfare      mecha_glow
    mecha_glow_v2           mecha_goddess_sci_fi    mecha_thunder_cyberpunk    mecha_winged_overlord    nuclear_03_3d
    nuclear_04_operational    pencil_sketch_06_mecha_3d    pencil_sketch_07_mecha_blueprint    pencil_sketch_08_split_diagram    pencil_sketch_09_fighter_design
    transformers_optimus_prime

📁 [anime_forge]
----------------------------------------------------------------------
  📂 art_nude/ (5 个)
    bijin_ga                intimate                kamasutra               oiran                   shunga
  📂 costume/ (1 个)
    kimono
  📂 dog/ (1 个)
    shiba
  📂 dream/ (1 个)
    liaozhai
  📂 furniture/ (1 个)
    cabinet
  📂 general/ (66 个)
    ancient_chinese_ladies_sketch    ancient_tree_temple_sketch    anime_figures           anime_greyscale_portrait    anime_portrait
    autumn_anime_portrait    bag_blueprint           bird_sketch             cat_sketch              chinese_ink_animals
    chinese_ink_cats        chinese_pattern_flower    classical_chinese_lineart    countryside_ink_lineart    crane_sketch
    divine_cranes_oriental    dog_sketch              dragon_sketch           dragon_sketch_v2        dragon_sketch_v3
    dragon_vertical_sketch    dragon_western_sketch    eastern_art_peacock_lotus    flower_sketch           goat_sketch
    gundam_sketch           hermit_ink_lineart      horse_sketch            jewelry_blueprint       koi_sketch
    mecha                   mecha_3d_prototype_dynamic    mecha_blueprint         mecha_chinese_warrior    mecha_dark_queen
    mecha_girl_doll_kit     mecha_girl_doll_series    mecha_girl_warfare      mecha_glow              mecha_glow_v2
    mecha_goddess_sci_fi    mecha_sketch            mecha_sketch_v2         monkey_sketch           nuclear_01_sketch
    nuclear_02_exploded     ox_sketch               pencil_sketch_01_fashion    pencil_sketch_02_anatomy    pencil_sketch_03_mecha
    pencil_sketch_04_atmosphere    pencil_sketch_05_minimal    pencil_sketch_06_mecha_3d    pencil_sketch_07_mecha_blueprint    pencil_sketch_08_split_diagram
    pencil_sketch_09_fighter_design    pig_sketch              rabbit_sketch           rat_sketch              rider_sketch
    rooster_sketch          sketch_fashion_designer    sketch_portrait         snake_sketch            tiger_sketch
    transformers_optimus_prime
  📂 genji/ (2 个)
    byobu_emaki             heian_court
  📂 incense/ (3 个)
    incense_appreciation    incense_gathering       incense_wood
  📂 japanese/ (2 个)
    emaki                   ukiyo_e
  📂 medicine/ (3 个)
    acupuncture             herbal                  physician
  📂 modern/ (6 个)
    cyber_chinese           future_tang             guochao                 ink_tech                mecha_classic
    new_chinese
  📂 music/ (1 个)
    bells
  📂 musician/ (1 个)
    shikuang
  📂 object/ (1 个)
    bronze
  📂 pattern/ (1 个)
    taotie
  📂 war/ (6 个)
    ambush                  cavalry                 military_camp           naval_battle            siege
    triumph
  📂 yokai/ (28 个)
    abe_no_seimei           bakeneko                biwa_bokuboku           chochin_obake           daitengu
    hidesato                hone_onna               hyakki_yagyo            jorogumo                kappa
    kasa_obake              kitsune                 kitsunebi               kiyohime                koto_furunushi
    minamoto_no_raiko       nekomata                nue                     nure_onna               nurikabe
    onibi                   rokurokubi              tamamo_no_mae           tengu                   watanabe_no_tsuna
    yuki_onna               yuurei                  zashiki_warashi

📁 [carving_forge]
----------------------------------------------------------------------
  📂 art_nude/ (8 个)
    bijin_ga                chungong                intimate                kamasutra               noh_mask
    oiran                   shunga                  shunga2
  📂 costume/ (1 个)
    kimono
  📂 dog/ (1 个)
    shiba
  📂 folklore/ (1 个)
    new_year_print
  📂 general/ (6 个)
    ancient_tree_temple_sketch    cat_sketch              chinese_ink_bird        cn_painting_art         countryside_ink_lineart
    sketch_fashion_designer
  📂 gufeng/ (1 个)
    gong_bi
  📂 japanese/ (1 个)
    ukiyo_e
  📂 object/ (1 个)
    jade
  📂 yokai/ (31 个)
    abe_no_seimei           bakeneko                biwa_bokuboku           chochin_obake           daitengu
    hidesato                hone_onna               hyakki_yagyo            ibaraki_doji            jorogumo
    kappa                   kasa_obake              kitsune                 kitsunebi               kiyohime
    koto_furunushi          minamoto_no_raiko       nekomata                nue                     nure_onna
    nurikabe                oni                     onibi                   rokurokubi              shuten_doji
    tamamo_no_mae           tengu                   watanabe_no_tsuna       yuki_onna               yuurei
    zashiki_warashi

📁 [figure_forge]
----------------------------------------------------------------------
  📂 art_nude/ (26 个)
    apsara                  apsara2                 baroque                 bijin_ga                chungong
    degas_pastel            heian_emaki             heian_emaki2            impressionist           impressionist2
    intimate                kamasutra               klimt                   modigliani              noh_dancer
    oiran                   realism                 renaissance             rubens                  schiele
    shunga                  shunga2                 song_painting           venetian                watto_fete
    watto_fete2
  📂 buddhism/ (1 个)
    bodhisattva
  📂 costume/ (2 个)
    hanfu                   nomad
  📂 dynasty/ (2 个)
    qin_han                 wei_jin
  📂 figure/ (1 个)
    literati
  📂 folklore/ (1 个)
    sugar_figure
  📂 furniture/ (1 个)
    couch
  📂 general/ (72 个)
    ancient_chinese_ladies_sketch    ancient_tree_temple_sketch    anime_figures           bag_blueprint           bird_sketch
    cat_sketch              chinese_ink_animals     chinese_ink_bird        chinese_ink_cats        chinese_landscape_master
    chinese_pattern_flower    city_sketch             classical_chinese_lineart    cn_painting_art         cosplay_mecha_samurai
    countryside_ink_lineart    crane_sketch            divine_cranes_oriental    dog_sketch              dragon_sketch
    dragon_sketch_v3        dragon_vertical_sketch    dragon_western_sketch    eva_sketch              farm_harvest_girl
    flower_sketch           gits_sketch             goat_sketch             gundam_sketch           hermit_ink_lineart
    horse_sketch            japanese_baseball_girl    jewelry_blueprint       jewelry_showcase        koi_sketch
    mecha_3d_prototype_dynamic    mecha_blueprint         mecha_chinese_warrior    mecha_dark_queen        mecha_girl_doll_kit
    mecha_girl_doll_series    mecha_girl_ultra_expansion    mecha_glow              mecha_glow_v2           mecha_sketch
    mecha_sketch_v2         mecha_vf_gunpla         monkey_sketch           nuclear_01_sketch       nuclear_02_exploded
    nuclear_03_3d           ox_sketch               pencil_sketch_01_fashion    pencil_sketch_02_anatomy    pencil_sketch_03_mecha
    pencil_sketch_04_atmosphere    pencil_sketch_05_minimal    pencil_sketch_06_mecha_3d    pencil_sketch_07_mecha_blueprint    pencil_sketch_08_split_diagram
    pencil_sketch_09_fighter_design    pig_sketch              rabbit_sketch           rat_sketch              rider_sketch
    rooster_sketch          snake_sketch            tiger_sketch            transformers_optimus_prime    transformers_sketch
    watch_blueprint         work_avatar
  📂 genji/ (4 个)
    byobu_emaki             cherry_blossom          heian_court             moon_viewing
  📂 gufeng/ (3 个)
    bai_miao                jian_bi                 shui_mo
  📂 japanese/ (2 个)
    emaki                   sumi_e
  📂 literati_gathering/ (6 个)
    bamboo_seven            lanting                 qushui                  spring_pavilion         xishan
    zui_weng
  📂 music/ (4 个)
    dance                   flute                   guqin                   pipa
  📂 musician/ (1 个)
    cai_wenji
  📂 opera/ (2 个)
    kunqu                   sichuan_opera
  📂 tang/ (2 个)
    dunhuang                tang_beauty
  📂 vehicle/ (2 个)
    cart                    sedan_chair
  📂 yokai/ (2 个)
    hyakki_yagyo            yuki_onna

📁 [mecha_forge]
----------------------------------------------------------------------
  📂 dynasty/ (3 个)
    qin_han                 republican              sui_tang
  📂 figure/ (1 个)
    warrior
  📂 general/ (35 个)
    anime_portrait          cosplay_mecha_samurai    eva_sketch              gits_sketch             gundam_sketch
    mecha                   mecha_3d_prototype_dynamic    mecha_blueprint         mecha_chinese_warrior    mecha_dark_queen
    mecha_girl_doll_kit     mecha_girl_doll_series    mecha_girl_ultra_expansion    mecha_girl_warfare      mecha_glow
    mecha_glow_v2           mecha_goddess_sci_fi    mecha_sketch            mecha_sketch_v2         mecha_thunder_cyberpunk
    mecha_vf_gunpla         mecha_winged_overlord    nuclear_01_sketch       nuclear_02_exploded     nuclear_03_3d
    nuclear_04_operational    pencil_sketch_03_mecha    pencil_sketch_06_mecha_3d    pencil_sketch_07_mecha_blueprint    pencil_sketch_08_split_diagram
    pencil_sketch_09_fighter_design    rider_sketch            transformers_optimus_prime    transformers_sketch     watch_blueprint
  📂 japanese/ (1 个)
    ukiyo_e
  📂 modern/ (4 个)
    cyber_chinese           future_tang             guochao                 mecha_classic
  📂 weapon/ (1 个)
    armor
  📂 yokai/ (4 个)
    hidesato                minamoto_no_raiko       oni                     watanabe_no_tsuna

📁 [mythology_forge]
----------------------------------------------------------------------
  📂 architecture/ (2 个)
    pagoda                  temple
  📂 art_nude/ (9 个)
    apsara                  apsara2                 baroque                 klimt                   noh_dancer
    noh_mask                renaissance             rubens                  venetian
  📂 astrology/ (6 个)
    big_dipper              celestial_phenomena     milky_way               star_officials          sun_moon
    twenty_eight_mansions
  📂 beast/ (1 个)
    lion
  📂 buddhism/ (5 个)
    arhat                   bodhisattva             buddha                  immortal_land           taoist
  📂 costume/ (2 个)
    crown                   tang_dress
  📂 dance/ (6 个)
    drum_dance              huxuan                  nichang                 startled_swan           sword_dance
    white_ramie
  📂 dream/ (2 个)
    immortal_dream          liaozhai
  📂 dynasty/ (2 个)
    qin_han                 sui_tang
  📂 figure/ (3 个)
    immortal                monk                    warrior
  📂 flower_arrangement/ (2 个)
    ikenobo                 rikka
  📂 folklore/ (2 个)
    new_year_print          sugar_figure
  📂 furniture/ (1 个)
    small_table
  📂 general/ (11 个)
    ancient_tree_temple_sketch    calligraphy_art         chinese_ink             city_sketch             classical_chinese_lineart
    divine_cranes_oriental    hermit_ink_lineart      mecha_chinese_warrior    mecha_goddess_sci_fi    mecha_winged_overlord
    pure_serene_safe
  📂 genji/ (2 个)
    byobu_emaki             cherry_blossom
  📂 gufeng/ (3 个)
    bai_miao                jian_bi                 qing_lv
  📂 incense/ (4 个)
    incense_ceremony        incense_gathering       incense_utensils        incense_wood
  📂 japanese/ (1 个)
    emaki
  📂 landscape/ (4 个)
    cloud_sea               qinglv_shanshui         shanshui_ink            snow_landscape
  📂 medicine/ (2 个)
    alchemy                 medicine_king
  📂 modern/ (3 个)
    cyber_chinese           future_tang             mecha_classic
  📂 mountain/ (3 个)
    cave                    cliff                   peaks
  📂 music/ (3 个)
    bells                   dance                   pipa
  📂 musician/ (3 个)
    cai_wenji               gongsun_daniang         li_guinian
  📂 mythical/ (1 个)
    white_tiger
  📂 object/ (2 个)
    incense                 jade
  📂 opera/ (1 个)
    opera_mask
  📂 pattern/ (3 个)
    baoxiang_flower         cloud_pattern           taotie
  📂 region/ (3 个)
    bashu                   xiyu                    zhongyuan
  📂 season/ (1 个)
    winter
  📂 tang/ (3 个)
    dunhuang                feitian                 tang_palace
  📂 tea_ceremony/ (2 个)
    matcha                  zen_tea
  📂 tree/ (1 个)
    pine
  📂 water/ (1 个)
    lake
  📂 weapon/ (5 个)
    armor                   bow                     halberd                 saber                   spear
  📂 weather/ (3 个)
    mist                    rain                    snow
  📂 yokai/ (25 个)
    abe_no_seimei           biwa_bokuboku           chochin_obake           daitengu                hidesato
    hone_onna               hyakki_yagyo            ibaraki_doji            jorogumo                kappa
    kasa_obake              kitsune                 kiyohime                koto_furunushi          minamoto_no_raiko
    nekomata                nue                     nurikabe                oni                     onibi
    rokurokubi              tengu                   watanabe_no_tsuna       yuki_onna               yuurei

📁 [oriental_forge]
----------------------------------------------------------------------
  📂 architecture/ (6 个)
    bridge                  garden                  pagoda                  palace                  temple
    village
  📂 art_nude/ (22 个)
    apsara                  apsara2                 bijin_ga                chungong                heian_emaki
    heian_emaki2            impressionist           impressionist2          intimate                kamasutra
    noh_dancer              noh_mask                oiran                   persian                 renaissance
    rococo                  rubens                  shunga                  shunga2                 song_painting
    watto_fete              watto_fete2
  📂 astrology/ (6 个)
    big_dipper              celestial_phenomena     milky_way               star_officials          sun_moon
    twenty_eight_mansions
  📂 beast/ (6 个)
    deer                    dragon                  horse                   lion                    qilin
    tiger
  📂 bird/ (6 个)
    crane                   eagle                   mandarin_duck           phoenix                 sparrow
    swallow
  📂 buddhism/ (6 个)
    arhat                   bodhisattva             buddha                  chan                    immortal_land
    taoist
  📂 calligraphy/ (6 个)
    caoshu                  kaishu                  kuangcao                lishu                   xingshu
    zhuanshu
  📂 cat/ (7 个)
    cat_and_butterfly       cat_and_fish            cat_and_flowers         cat_playing             cat_sitting
    cat_sleeping            persian
  📂 costume/ (6 个)
    crown                   hanfu                   kimono                  nomad                   ornament
    tang_dress
  📂 dance/ (6 个)
    drum_dance              huxuan                  nichang                 startled_swan           sword_dance
    white_ramie
  📂 dog/ (7 个)
    dog_and_butterfly       dog_and_fish            dog_and_flowers         dog_playing             dog_sitting
    dog_sleeping            shiba
  📂 dream/ (6 个)
    illusion                immortal_dream          liaozhai                south_branch            yellow_millet
    zhuangzi_butterfly
  📂 dynasty/ (6 个)
    ming_qing               qin_han                 republican              song_yuan               sui_tang
    wei_jin
  📂 festival/ (6 个)
    double_ninth            dragon_boat             lantern_festival        mid_autumn              qixi
    spring_festival
  📂 figure/ (6 个)
    beauty                  children                immortal                literati                monk
    warrior
  📂 fish/ (6 个)
    carp                    crab                    goldfish                koi                     mandarin_fish
    shrimp
  📂 flower/ (6 个)
    bamboo                  chrysanthemum           lotus                   orchid                  peony
    plum_blossom
  📂 flower_arrangement/ (5 个)
    ikenobo                 nageire                 ohara                   rikka                   shoka
  📂 folklore/ (6 个)
    new_year_print          paper_cutting           puppet                  shadow_puppet           sugar_figure
    yangko
  📂 fruit/ (6 个)
    grape                   lychee                  peach                   persimmon               plum
    pomegranate
  📂 furniture/ (6 个)
    cabinet                 chair                   couch                   screen                  small_table
    table
  📂 general/ (43 个)
    ancient_chinese_ladies_sketch    ancient_tree_temple_sketch    anime_figures           anime_portrait          autumn_lotus_dragonfly
    calligraphy_art         cat_sketch              chinese_ink             chinese_ink_animals     chinese_ink_bird
    chinese_ink_cats        chinese_landscape_master    chinese_pattern_flower    classical_chinese_lineart    cn_painting_art
    countryside_ink_lineart    crane_sketch            divine_cranes_oriental    dog_sketch              dragon_sketch
    dragon_vertical_sketch    dragon_western_sketch    eastern_art_peacock_lotus    goat_sketch             hermit_ink_lineart
    horse_sketch            koi_sketch              mecha_chinese_warrior    mecha_girl_doll_series    mecha_girl_ultra_expansion
    mecha_goddess_sci_fi    monkey_sketch           ox_sketch               pencil_sketch_03_mecha    pig_sketch
    pure_serene_safe        rabbit_sketch           rat_sketch              rooster_sketch          sketch_fashion_designer
    snake_sketch            tiger_sketch            transformers_optimus_prime
  📂 genji/ (5 个)
    byobu_emaki             cherry_blossom          heian_court             junihitoe               moon_viewing
  📂 gufeng/ (5 个)
    bai_miao                gong_bi                 jian_bi                 qing_lv                 shui_mo
  📂 incense/ (6 个)
    blended_incense         incense_appreciation    incense_ceremony        incense_gathering       incense_utensils
    incense_wood
  📂 insect/ (6 个)
    butterfly               cicada                  cricket                 dragonfly               firefly
    mantis
  📂 japanese/ (5 个)
    byobu_e                 emaki                   nihonga                 sumi_e                  ukiyo_e
  📂 landscape/ (6 个)
    autumn_mountain         cloud_sea               qinglv_shanshui         shanshui_ink            snow_landscape
    waterfall_gorge
  📂 literati_gathering/ (6 个)
    bamboo_seven            lanting                 qushui                  spring_pavilion         xishan
    zui_weng
  📂 medicine/ (6 个)
    acupuncture             alchemy                 herb_gathering          herbal                  medicine_king
    physician
  📂 modern/ (5 个)
    cyber_chinese           future_tang             ink_tech                mecha_classic           new_chinese
  📂 mountain/ (5 个)
    cave                    cliff                   cliff_path              peaks                   rocks
  📂 music/ (5 个)
    bells                   dance                   flute                   guqin                   pipa
  📂 musician/ (6 个)
    boya                    cai_wenji               gongsun_daniang         ji_kang                 li_guinian
    shikuang
  📂 mythical/ (6 个)
    black_tortoise          dragon                  phoenix                 qilin                   vermilion_bird
    white_tiger
  📂 object/ (6 个)
    bronze                  incense                 jade                    porcelain               qin
    tea
  📂 opera/ (6 个)
    beijing_opera           huangmei                kunqu                   opera_mask              sichuan_opera
    yue_opera
  📂 pattern/ (5 个)
    baoxiang_flower         cloud_pattern           dragon_pattern          interlocking_floral     taotie
  📂 region/ (6 个)
    bashu                   jiangnan                lingnan                 saibei                  xiyu
    zhongyuan
  📂 season/ (4 个)
    autumn                  spring                  summer                  winter
  📂 tang/ (5 个)
    dunhuang                feitian                 tang_beauty             tang_horse              tang_palace
  📂 tea_ceremony/ (6 个)
    gongfu                  literati_tea            matcha                  sencha                  tea_contest
    zen_tea
  📂 tree/ (6 个)
    bamboo                  banyan                  maple                   pine                    plum_tree
    willow
  📂 vegetable/ (5 个)
    bamboo_shoot            cabbage                 gourd                   lotus_root              radish
  📂 vehicle/ (6 个)
    boat                    camel                   cart                    horse                   raft
    sedan_chair
  📂 war/ (6 个)
    ambush                  cavalry                 military_camp           naval_battle            siege
    triumph
  📂 water/ (5 个)
    lake                    river                   sea                     spring                  stream
  📂 weapon/ (6 个)
    armor                   bow                     halberd                 saber                   spear
    sword
  📂 weather/ (6 个)
    mist                    rain                    rainbow                 snow                    thunder
    wind
  📂 yokai/ (31 个)
    abe_no_seimei           bakeneko                biwa_bokuboku           chochin_obake           daitengu
    hidesato                hone_onna               hyakki_yagyo            ibaraki_doji            jorogumo
    kappa                   kasa_obake              kitsune                 kitsunebi               kiyohime
    koto_furunushi          minamoto_no_raiko       nekomata                nue                     nure_onna
    nurikabe                oni                     onibi                   rokurokubi              shuten_doji
    tamamo_no_mae           tengu                   watanabe_no_tsuna       yuki_onna               yuurei
    zashiki_warashi

📁 [painting_forge]
----------------------------------------------------------------------
  📂 art_nude/ (7 个)
    baroque                 impressionist2          klimt                   renaissance             rubens
    schiele                 venetian
  📂 calligraphy/ (1 个)
    kaishu
  📂 general/ (33 个)
    ancient_chinese_ladies_sketch    anime_portrait          calligraphy_art         casual_daily_life_girl    cat_sketch
    chinese_ink             chinese_ink_animals     chinese_ink_bird        chinese_ink_cats        chinese_landscape_master
    chinese_pattern_flower    cn_painting_art         crane_sketch            divine_cranes_oriental    dog_sketch
    eastern_art_peacock_lotus    gallery_elegant_safe    goat_sketch             healing_landscape       hermit_ink_lineart
    horse_sketch            koi_sketch              mecha_3d_prototype_dynamic    mecha_dark_queen        mecha_girl_doll_kit
    monkey_sketch           ox_sketch               pig_sketch              rabbit_sketch           rat_sketch
    rooster_sketch          snake_sketch            tiger_sketch
  📂 gufeng/ (2 个)
    jian_bi                 shui_mo
  📂 japanese/ (1 个)
    sumi_e
  📂 yokai/ (3 个)
    ibaraki_doji            oni                     shuten_doji

📁 [photography_forge]
----------------------------------------------------------------------
  📂 architecture/ (6 个)
    bridge                  garden                  pagoda                  palace                  temple
    village
  📂 astrology/ (6 个)
    big_dipper              celestial_phenomena     milky_way               star_officials          sun_moon
    twenty_eight_mansions
  📂 beast/ (6 个)
    deer                    dragon                  horse                   lion                    qilin
    tiger
  📂 bird/ (6 个)
    crane                   eagle                   mandarin_duck           phoenix                 sparrow
    swallow
  📂 buddhism/ (6 个)
    arhat                   bodhisattva             buddha                  chan                    immortal_land
    taoist
  📂 calligraphy/ (6 个)
    caoshu                  kaishu                  kuangcao                lishu                   xingshu
    zhuanshu
  📂 cat/ (7 个)
    cat_and_butterfly       cat_and_fish            cat_and_flowers         cat_playing             cat_sitting
    cat_sleeping            persian
  📂 costume/ (6 个)
    crown                   hanfu                   kimono                  nomad                   ornament
    tang_dress
  📂 dance/ (6 个)
    drum_dance              huxuan                  nichang                 startled_swan           sword_dance
    white_ramie
  📂 dog/ (7 个)
    dog_and_butterfly       dog_and_fish            dog_and_flowers         dog_playing             dog_sitting
    dog_sleeping            shiba
  📂 dream/ (6 个)
    illusion                immortal_dream          liaozhai                south_branch            yellow_millet
    zhuangzi_butterfly
  📂 dynasty/ (6 个)
    ming_qing               qin_han                 republican              song_yuan               sui_tang
    wei_jin
  📂 festival/ (6 个)
    double_ninth            dragon_boat             lantern_festival        mid_autumn              qixi
    spring_festival
  📂 figure/ (6 个)
    beauty                  children                immortal                literati                monk
    warrior
  📂 fish/ (6 个)
    carp                    crab                    goldfish                koi                     mandarin_fish
    shrimp
  📂 flower/ (6 个)
    bamboo                  chrysanthemum           lotus                   orchid                  peony
    plum_blossom
  📂 flower_arrangement/ (6 个)
    ikenobo                 nageire                 ohara                   rikka                   shoka
    sogetsu
  📂 folklore/ (6 个)
    new_year_print          paper_cutting           puppet                  shadow_puppet           sugar_figure
    yangko
  📂 fruit/ (6 个)
    grape                   lychee                  peach                   persimmon               plum
    pomegranate
  📂 furniture/ (6 个)
    cabinet                 chair                   couch                   screen                  small_table
    table
  📂 general/ (99 个)
    ancient_chinese_ladies_sketch    ancient_tree_temple_sketch    anime_figures           anime_greyscale_portrait    anime_portrait
    autumn_anime_portrait    autumn_lotus_dragonfly    bag_blueprint           beach_resort_swimwear    bird_sketch
    calligraphy_art         casual_daily_life_girl    cat_sketch              chinese_ink             chinese_ink_animals
    chinese_ink_bird        chinese_ink_cats        chinese_landscape_master    chinese_pattern_flower    city_sketch
    classical_chinese_lineart    cn_painting_art         cosplay_mecha_samurai    countryside_ink_lineart    crane_sketch
    divine_cranes_oriental    dog_sketch              dragon_sketch           dragon_sketch_v2        dragon_sketch_v3
    dragon_vertical_sketch    dragon_western_sketch    eastern_art_peacock_lotus    eva_sketch              farm_harvest_girl
    flower_sketch           gallery_elegant         gallery_elegant_safe    gits_sketch             goat_sketch
    gundam_sketch           healing_landscape       hermit_ink_lineart      horse_sketch            human_portrait_sketch
    human_sketch_frame      japanese_baseball_girl    jewelry_blueprint       jewelry_showcase        koi_sketch
    mecha                   mecha_3d_prototype_dynamic    mecha_blueprint         mecha_chinese_warrior    mecha_dark_queen
    mecha_girl_doll_kit     mecha_girl_doll_series    mecha_girl_ultra_expansion    mecha_girl_warfare      mecha_glow
    mecha_glow_v2           mecha_goddess_sci_fi    mecha_sketch            mecha_sketch_v2         mecha_thunder_cyberpunk
    mecha_vf_gunpla         mecha_winged_overlord    medical_professional_nurse    monkey_sketch           nature_outdoor_girl
    nuclear_01_sketch       nuclear_02_exploded     nuclear_03_3d           nuclear_04_operational    ox_sketch
    pencil_sketch_01_fashion    pencil_sketch_02_anatomy    pencil_sketch_03_mecha    pencil_sketch_04_atmosphere    pencil_sketch_05_minimal
    pencil_sketch_06_mecha_3d    pencil_sketch_07_mecha_blueprint    pencil_sketch_08_split_diagram    pencil_sketch_09_fighter_design    pig_sketch
    pure_serene             pure_serene_safe        rabbit_sketch           rat_sketch              rider_sketch
    rooster_sketch          sketch_fashion_designer    sketch_portrait         snake_sketch            tiger_sketch
    transformers_optimus_prime    transformers_sketch     watch_blueprint         work_avatar
  📂 incense/ (6 个)
    blended_incense         incense_appreciation    incense_ceremony        incense_gathering       incense_utensils
    incense_wood
  📂 insect/ (6 个)
    butterfly               cicada                  cricket                 dragonfly               firefly
    mantis
  📂 landscape/ (6 个)
    autumn_mountain         cloud_sea               qinglv_shanshui         shanshui_ink            snow_landscape
    waterfall_gorge
  📂 literati_gathering/ (6 个)
    bamboo_seven            lanting                 qushui                  spring_pavilion         xishan
    zui_weng
  📂 medicine/ (6 个)
    acupuncture             alchemy                 herb_gathering          herbal                  medicine_king
    physician
  📂 modern/ (6 个)
    cyber_chinese           future_tang             guochao                 ink_tech                mecha_classic
    new_chinese
  📂 mountain/ (5 个)
    cave                    cliff                   cliff_path              peaks                   rocks
  📂 music/ (5 个)
    bells                   dance                   flute                   guqin                   pipa
  📂 musician/ (6 个)
    boya                    cai_wenji               gongsun_daniang         ji_kang                 li_guinian
    shikuang
  📂 mythical/ (6 个)
    black_tortoise          dragon                  phoenix                 qilin                   vermilion_bird
    white_tiger
  📂 object/ (6 个)
    bronze                  incense                 jade                    porcelain               qin
    tea
  📂 opera/ (6 个)
    beijing_opera           huangmei                kunqu                   opera_mask              sichuan_opera
    yue_opera
  📂 pattern/ (6 个)
    baoxiang_flower         cloud_pattern           dragon_pattern          hui_pattern             interlocking_floral
    taotie
  📂 region/ (6 个)
    bashu                   jiangnan                lingnan                 saibei                  xiyu
    zhongyuan
  📂 season/ (4 个)
    autumn                  spring                  summer                  winter
  📂 tea_ceremony/ (6 个)
    gongfu                  literati_tea            matcha                  sencha                  tea_contest
    zen_tea
  📂 tree/ (6 个)
    bamboo                  banyan                  maple                   pine                    plum_tree
    willow
  📂 vegetable/ (5 个)
    bamboo_shoot            cabbage                 gourd                   lotus_root              radish
  📂 vehicle/ (6 个)
    boat                    camel                   cart                    horse                   raft
    sedan_chair
  📂 war/ (6 个)
    ambush                  cavalry                 military_camp           naval_battle            siege
    triumph
  📂 water/ (5 个)
    lake                    river                   sea                     spring                  stream
  📂 weapon/ (6 个)
    armor                   bow                     halberd                 saber                   spear
    sword
  📂 weather/ (6 个)
    mist                    rain                    rainbow                 snow                    thunder
    wind
  📂 yokai/ (1 个)
    tengu

📁 [pixel_forge]
----------------------------------------------------------------------
  📂 general/ (2 个)
    nuclear_03_3d           pencil_sketch_09_fighter_design

📁 [poster_forge]
----------------------------------------------------------------------
  📂 dynasty/ (1 个)
    republican
  📂 general/ (6 个)
    chinese_pattern_flower    divine_cranes_oriental    dragon_sketch_v2        dragon_vertical_sketch    mecha_winged_overlord
    pencil_sketch_05_minimal
  📂 modern/ (4 个)
    cyber_chinese           future_tang             guochao                 mecha_classic
  📂 opera/ (4 个)
    beijing_opera           opera_mask              sichuan_opera           yue_opera

📁 [sculpture_forge]
----------------------------------------------------------------------
  📂 architecture/ (1 个)
    palace
  📂 art_nude/ (8 个)
    apsara                  apsara2                 kamasutra               modigliani              rococo
    rubens                  venetian                watto_fete
  📂 beast/ (1 个)
    qilin
  📂 bird/ (1 个)
    phoenix
  📂 calligraphy/ (1 个)
    zhuanshu
  📂 cat/ (1 个)
    persian
  📂 costume/ (1 个)
    tang_dress
  📂 figure/ (1 个)
    beauty
  📂 flower/ (1 个)
    peony
  📂 flower_arrangement/ (2 个)
    rikka                   sogetsu
  📂 furniture/ (1 个)
    small_table
  📂 general/ (25 个)
    ancient_tree_temple_sketch    anime_figures           anime_greyscale_portrait    anime_portrait          calligraphy_art
    cn_painting_art         gundam_sketch           mecha_3d_prototype_dynamic    mecha_dark_queen        mecha_girl_doll_kit
    mecha_girl_doll_series    mecha_girl_ultra_expansion    mecha_glow              mecha_glow_v2           mecha_thunder_cyberpunk
    mecha_vf_gunpla         mecha_winged_overlord    nuclear_03_3d           ox_sketch               pencil_sketch_02_anatomy
    pencil_sketch_06_mecha_3d    pencil_sketch_09_fighter_design    rooster_sketch          transformers_optimus_prime    transformers_sketch
  📂 gufeng/ (1 个)
    gong_bi
  📂 japanese/ (1 个)
    ukiyo_e
  📂 medicine/ (2 个)
    acupuncture             medicine_king
  📂 mountain/ (1 个)
    rocks
  📂 music/ (1 个)
    bells
  📂 object/ (2 个)
    bronze                  incense
  📂 pattern/ (2 个)
    hui_pattern             taotie
  📂 tang/ (4 个)
    dunhuang                feitian                 tang_beauty             tang_palace
  📂 yokai/ (10 个)
    bakeneko                daitengu                hone_onna               hyakki_yagyo            jorogumo
    kappa                   kitsune                 kitsunebi               tamamo_no_mae           tengu

📁 [sketch_forge]
----------------------------------------------------------------------
  📂 art_nude/ (2 个)
    modigliani              schiele
  📂 general/ (57 个)
    ancient_chinese_ladies_sketch    ancient_tree_temple_sketch    bag_blueprint           bird_sketch             cat_sketch
    chinese_ink_cats        chinese_pattern_flower    city_sketch             classical_chinese_lineart    countryside_ink_lineart
    crane_sketch            divine_cranes_oriental    dog_sketch              dragon_sketch           dragon_sketch_v2
    dragon_sketch_v3        dragon_vertical_sketch    dragon_western_sketch    eva_sketch              flower_sketch
    gits_sketch             goat_sketch             gundam_sketch           hermit_ink_lineart      horse_sketch
    human_portrait_sketch    human_sketch_frame      jewelry_blueprint       koi_sketch              mecha
    mecha_blueprint         mecha_sketch            mecha_sketch_v2         monkey_sketch           nuclear_01_sketch
    nuclear_02_exploded     ox_sketch               pencil_sketch_01_fashion    pencil_sketch_02_anatomy    pencil_sketch_03_mecha
    pencil_sketch_04_atmosphere    pencil_sketch_05_minimal    pencil_sketch_06_mecha_3d    pencil_sketch_07_mecha_blueprint    pencil_sketch_08_split_diagram
    pencil_sketch_09_fighter_design    pig_sketch              rabbit_sketch           rat_sketch              rider_sketch
    rooster_sketch          sketch_fashion_designer    sketch_portrait         snake_sketch            tiger_sketch
    transformers_sketch     watch_blueprint
  📂 gufeng/ (1 个)
    bai_miao

======================================================================
 统计: 13 个App分类, 219 个主题, 1430 个预设文件
======================================================================

💡 用法示例:
  python cli.py --app oriental_forge --theme region --preset dragon



E:\SD_OpenVINO\ForgeWorkspace>python apps/sd_generator/cli.py --app oriental_forge --theme region --preset dragon
SegDetector/UniformerDetector 不可用，请更新 controlnet-aux

======================================================================
🎨 SD Generator 启动
======================================================================
   ⚠️ 警告: 层 'view' 为空
✅ 提示词就绪: a dragon, with waves, in the sea, sky, clouds, sunrise, Chin...
ℹ️ 未指定模型，自动选择默认: DreamShaper_8_pruned
💻 本地模型: E:\SD_OpenVINO\models\sd-v1-5\DreamShaper_8_pruned.safetensors (sd15)
📐 分辨率: 512x768 | 步数: 20 | CFG: 7.5
⏳ 正在加载模型 (首次需 30-60 秒)...

============================================================
🚀 开始加载本地模型: DreamShaper_8_pruned.safetensors
📏 文件大小: 2033.83 MB
💻 目标设备: CPU
============================================================
   [1/3] 正在导入 diffusers 库...
   [2/3] 正在读取模型权重 (这步最慢，请耐心等待 30-60 秒)...
Fetching 11 files: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11/11 [00:00<00:00, 98.84it/s]
Reconstruction complete: |                                                                                                              |  0.00B /  0.00B
Download complete: :                                                                                                                             |  0.00B
Loading pipeline components...:   0%|                                                                                                          | 0/6 [00:00<?, ?it/s]There are modules in UNet2DConditionModel that should be kept in float32: []. Casting directly with `to()` can lead to inconsistent results; set `torch_dtype` in `from_pretrained()` instead to keep these modules in float32.██████████████████████████████████████████████▎                                | 4/6 [00:01<00:00,  3.87it/s]
                                                                                                                                                                     There are modules in AutoencoderKL that should be kept in float32: []. Casting directly with `to()` can lead to inconsistent results; set `torch_dtype` in `from_pretrained()` instead to keep these modules in float32.█████████████████████████████████████████████████████████████████████▋                | 5/6 [00:07<00:02,  2.12s/it]
Loading pipeline components...: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:07<00:00,  1.31s/it]
   [3/3] 正在应用内存优化 (VAE Slicing & Attention Slicing)...
   -> 管道初始化完成，准备就绪。100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:07<00:00,  1.66s/it]
✅ 模型加载完成！耗时: 9.81 秒
============================================================

✅ 模型加载完成，开始生成...
🎨 开始推理: a dragon, with waves, in the sea, sky, clouds, sun...
⚙️ 参数: steps=20, cfg=7.5, seed=3636815475
🔄 正在生成图片...
  0%|                                                                                                                                         | 0/20 [00:00<?, ?it/s]

  