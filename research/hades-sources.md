# 哈迪斯 PC 版资料与资源核验

核验日期：2026-10-04。范围为用户提供的 Steam Hades（第一代，App 1145360），不使用 Hades II 的数据。

- 中文名称、英文名称、作用说明：`Content/Game/Text/zh-CN/HelpText.zh-CN.sjson` 和对应英文文件。文字中的关键词、图标与数值变量转换为可直接阅读的文本。
- 祝福：`Content/Scripts/LootData.lua` 中各神祇的实际祝福池及 `LinkedUpgrades`，搭配 `TraitData.lua` 中的条件。双重祝福按 `OneFromEachSet` 列出每组可选前置；传奇及普通进阶祝福按 `OneOf` 列出条件，同时保留武器形态、冥夜之镜和互斥要求。
- 祝福数值：初始等级、普通稀有度；传奇与双重祝福按固定稀有度。区间值使用配置下限，实际可能在同一稀有度区间内浮动。混沌收录永久恩赐，随机诅咒以获取说明解释；没有将所有诅咒与恩赐的笛卡尔组合重复收录。
- 哈迪斯之援：`HadesShoutTrait` 与游戏中的冥王印玺说明，入口为装备信物，而非普通房间奖励。
- 武器形态与消耗：`WeaponUpgradeData.lua` 的六种武器、每种四个形态及 `Costs`。数值基于 `TraitData.lua`，按 `TraitScripts.lua` 的倍率、取整与显示规则计算。
- 外部基础值：`WeaponData.lua`、`Game/Weapons/*.sjson`、`Game/Projectiles/*.sjson`。特别核对喀戎的自定义倍率（4/5/6/7/8 支箭）、宙斯盾基础伤害（8/13/19/24/30）与赫拉掉落时间（10/8/6.67/6.15/5 秒）。
- 隐藏形态解锁：`NPCData.lua`、`LootData.lua`、`EnemyData.lua` 中各形态的唤醒对话要求；共用关羽揭示、相应武器投入五份泰坦之血，以及对应角色的对话触发条件。还需剧情对话排队，满足数值条件后不保证下次交谈立即触发。
- 图标和形态图片：`Game/Animations/GUIAnimations.sjson`、`PortraitAnimations.sjson` 的 `FilePath` 对应 `Win/Packages/GUI.pkg` 的子图集矩形。保存为站内 PNG，不在运行时读取用户安装目录或外链图片。
- 原始包解析使用 [deppth 项目](https://github.com/quaerus/deppth) 的只读 `PackageWithManifestReader`，安装版本对应提交 `52bb25a36637e6261dc7c44e8f2500fac3e30cc4`。

`app/data/hades.source.json` 保存文件 SHA-256、每个形态的配置、祝福前置关系与图集定位。源目录中存在模组，提取脚本不加载 `Mods` 或运行游戏启动脚本，只读取上述数据文件；本轮没有进入游戏逐个验证祝福出现概率。

官方游戏入口：[Supergiant Games](https://www.supergiantgames.com/games/hades/)、[Steam](https://store.steampowered.com/app/1145360/Hades/)。游戏图片与原始文本归原权利人所有。
