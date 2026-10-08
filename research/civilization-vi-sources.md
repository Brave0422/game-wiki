# 文明 VI 中文百科：来源与提取说明

采集日期：2026-10-05（北京时间）。规则集：**风云变幻 / RULESET_EXPANSION_2**。数据来自用户提供的本地 PC 游戏安装目录 `E:/SteamLibrary/steamapps/common/Sid Meier's Civilization VI`，采集过程只读游戏文件。

## 范围

| 分类 | 条目数 | 主要内容 |
| --- | ---: | --- |
| 文明 | 50 | 文明能力、可选领袖、特色单位／建筑／区域／改良设施 |
| 领袖 | 77 | 领袖能力、领导文明、历史议程、历史背景 |
| 单位 | 144 | 平民、陆海空战斗、支援、伟人类别；成本、战斗力、移动力、升级与前置 |
| 建筑 | 82 | 区域建筑、产出、维护、住房、宜居度、伟人点数与前置 |
| 奇观 | 53 | 世界奇观效果、地块条件、基础成本、解锁与历史背景 |
| 区域 | 35 | 常规及文明特色区域，效果、产出、基础成本与解锁 |
| 科技 | 77 | 时代、科技值、前置科技、解锁、尤里卡、原文效果与历史背景 |
| 市政 | 61 | 时代、文化值、前置市政、解锁、鼓舞、原文效果与历史背景 |
| 资源 | 52 | 12 种加成、33 种奢侈品、7 种战略资源；开发、积累、供电与特殊来源 |
| 机制 | 131 | 城市、外交、宗教、贸易、胜利、忠诚度、气候、电力、世界议会等原游戏教程 |
| **合计** | **762** | |

加载本地已安装的常规官方 DLC 和领袖包。排除情景、英雄与传奇、秘密结社等可选模式专属数据库；不把这些玩法的独立单位、建筑和机制混入常规目录。本轮没有单列政策、政体、城邦、伟人个人、改良设施和自然奇观目录；相关内容通过所属文明、科技／市政解锁和机制介绍显示。

52 种资源包括六种不会自然生成在地图上的特殊奢侈品。牛仔裤、香水、化妆品、玩具通过对应大商人激活获得；肉桂与丁香来自桑给巴尔城邦宗主国能力。这些条目已明确特殊来源，不使用普通地块资源的获取说明。

## 本地原始来源

- `Base/Assets/Gameplay/Data/Schema/01_GameplaySchema.sql`：原游戏 SQLite 表结构、字段默认值。
- `Base/Assets/Gameplay/Data/*.xml`：原版文明、领袖、单位、建筑、区域、科技、市政、资源与百科章节。
- `Base/Assets/Text/Vanilla_zh_Hans_CN.xml`：原版简体中文名称、说明与历史背景。
- `Base/Assets/Text/en_US/*.xml`：英文名称（支持 `BaseGameText` 节点）。
- `DLC/*/*.modinfo`：数据库／文本动作、规则集条件、加载次序与文件优先级。
- `DLC/Expansion2/Data/Expansion2_Schema.sql` 与有效数据库动作：风云变幻规则，以及适用于风云变幻的迭起兴衰内容。
- `DLC/*/Text/*Translations*.xml`：官方 DLC 中文翻译与规则集文本覆盖。
- `Base/Assets/UI/Civilopedia/CivilopediaPage_Unit.lua`：百科的单位购买成本展示公式。金币基准为 `Cost × GOLD_PURCHASE_MULTIPLIER × GOLD_EQUIVALENT_OTHER_YIELDS`，其他购买产出为 `Cost × GOLD_EQUIVALENT_OTHER_YIELDS`；本安装两参数均为 2。因此使徒初始基准信仰成本为 400，传教士为 150。只能购买的单位不会被误列生产力成本；递增购买模型另附说明。

`app/data/civilization-vi.source.json` 登记 710 个实际读取文件的相对路径与 SHA-256，每条目录项保留源类型、原游戏图标名、源文件与在线对应页。脚本发现 24 个被 `.modinfo` 引用、但此安装未提供的可选文件（包括 China 专用翻译及部分包的辅助文件）；清单保留在 `extractionWarnings` 中。已入库中文词条没有缺失的名称或说明、未解析格式标记或占位符。可恢复的官方别名记录在 `resolvedLocalizationAliases` 中。

## 提取与规则合并

提取脚本使用 Python 标准库，在内存 SQLite 中应用 XML 的新增、替换、更新和删除，以及 SQL 文件。数据库字段按 SQLite 规则忽略大小写；游戏内文件保持不变。官方动作按加载次序与文件优先级合并，条件采用风云变幻及本安装常规官方内容。

本地化 `Delete` 没有指定语言时，删除全部语言的旧文本，再应用当前资料片的翻译。这一点用于保证科技胜利只呈现风云变幻的卫星、登月、火星殖民、系外行星探索和激光站流程，不残留原版分开的火星模块段落。环境效果和世界议会的自定义多章节内容也一并收录。

原游戏格式标记被转换为普通段落和中文单位，已带中文标签的图标只移除图标占位，不重复添加单位。能力说明和历史背景直接取自本地官方中文文本；缺少独立说明的科技、市政、建筑和资源，使用数据库关系生成解锁／产出说明并保留游戏历史段落。数字来自规则字段，不推测额外效果。

属性展示标准速度的规则基础值；实际费用、战斗、产出和资源积累会受到游戏速度、时代、政策、文明能力、总督、难度及其他效果影响。脚本没有模拟一场对局中的全部动态修正。

## 在线参考与图像

用户提供的 [文明百科 · 风云变幻](https://www.civilopedia.net/zh-CN/gathering-storm/concepts/intro/) 用于核对章节、对应页和视觉主题。每条词条提供同源在线参考链接；正文采集于本地游戏文件，没有另行复制第三方攻略文章。

在线抽样核对了 [使徒](https://www.civilopedia.net/zh-CN/gathering-storm/units/unit_apostle/)、[蒸汽动力](https://www.civilopedia.net/zh-CN/gathering-storm/technologies/tech_steam_power/) 与 [科技胜利](https://www.civilopedia.net/zh-CN/gathering-storm/concepts/victory_3/)，确认宗教单位前置建筑与初始购买成本、蒸汽动力水运移动力效果及铁路解锁、风云变幻科技胜利流程。

真实游戏图标通过独立 `scripts/extract-civilization-vi-assets.py` 采集并保存到 `public/images/civilization-vi/`。该脚本优先解析本地原游戏图标名／别名，并从文明百科公开静态图像源获取对应图标；`image-map.json` 保留 URL、文件 SHA-256、尺寸和来源映射。机制条目复用真实百科章头图标。

## 重新生成

```powershell
python scripts/extract-civilization-vi.py --game "E:/SteamLibrary/steamapps/common/Sid Meier's Civilization VI"
python scripts/extract-civilization-vi-assets.py --manifest app/data/civilization-vi.source.json
python scripts/extract-civilization-vi.py --game "E:/SteamLibrary/steamapps/common/Sid Meier's Civilization VI"
node scripts/verify-data.mjs
```

第一步生成目录和待采集图标清单；第二步采集真实 PNG；第三步应用图片映射；最后验证目录、图像、来源和关键风云变幻规则。本地化残留标记、重复 ID、重复属性标签或缺失图像都会被校验发现。
