# 霓虹深渊 PC 原版资料核验记录

检索日期：2026-10-04。范围为 Steam App **788100** 的 Neon Abyss；不使用《霓虹深渊：无限》手游与 Neon Abyss 2 的资料。

## 数据来源分工

- 游戏内中文名称、英文名称、基础效果和图标：用户提供的本地游戏安装资源，只读提取。文件中的名称已用于覆盖资料的精确对齐。
- 角色：从 `CharacterList` 和 `CharacterSkinList` 的实际引用提取 11 个基础角色与 10 个异装，保存初始资源、初始武器、技能文本和头像。布若为 PC 版联动角色；不混用手游角色资料。详情及完整配置见 `neon-abyss.characters.source.json`。
- 获取条件、进化关系、效果补充：外部资料逐条核验后写入 `app/data/neon-abyss.supplements.json`。
- 攻略：自主概括的三篇组合/操作思路，保留对应来源，见 `app/data/neon-abyss.guides.json`。
- 商店视觉：从官方 Steam 商店实际图片链接下载的 header，保存为 `public/images/neon-abyss/steam-header.jpg`。

## 官方来源

1. [Steam 原版商店](https://store.steampowered.com/app/788100/Neon_Abyss/)：核验标题、开发者 Veewo Games、App ID 和官方视觉。
   - header 原始 URL：<https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/788100/7105869c3cf24c4fe65284ba978e23d2f691c372/header.jpg?t=1790587946>
   - 已下载并目视核验：原版霓虹深渊标题、霓虹人物视觉，460×215。
2. [Veewo 中文官网更新记录](https://www.veewo.com/na-log?lang=zh)：确认老大哥只免疫自身爆炸、钢铁意志免疫全部爆炸。页面同时保留多个旧测试版本，不能把旧神币概率/次数直接当作当前版结论。
3. [Steam · Call of Hades 1.4 更新](https://steamcommunity.com/games/788100/announcements/detail/3096765393287424721)：确认 Peter、Dr. Manhattan、Agent Grey 同时存在后合体。实际内容通过 Steam 公共新闻 API 返回的官方公告核验，API 的 externalpost 链接已跟随重定向核验并使用最终公告链接。
4. [Steam · Lovable Rogues Pack](https://store.steampowered.com/app/1262000/Neon_Abyss__Lovable_Rogues_Pack/)：确认纱夜和阿米尔属于该 DLC。此轮只给能够与本地名称精确对齐的粉焰补充条件。
5. [Steam · Alter Ego](https://store.steampowered.com/app/1518790/Neon_Abyss__Alter_Ego/)：确认异装角色拥有不同技能，纱夜和阿米尔的异装仍需 Lovable Rogues DLC。没有把“全部武器需要该 DLC”等未被支持的说法写入词条。
6. [Steam · Chrono Trap](https://store.steampowered.com/app/1851340/Neon_Abyss__Chrono_Trap/)：确认该 DLC 增加无尽模式与 Chronos；未发现其与本轮特定道具/宠物绑定的可信证据，因此不虚构 DLC 限定列表。
7. [Steam · Update 1.5.2](https://steamcommunity.com/games/788100/announcements/detail/3469488996666829972)：确认增加 Mystery Item Room；公告没有给出新宠物逐条获取方式。

公共新闻 API：<https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=788100&count=100&maxlength=0&format=json>。仅在检索期读取，不作为网站运行依赖。

## 社区 Wiki 来源

站点名带有 Official Wiki，但内容由玩家维护，不能表述为开发者逐条审核。多数页面标注 Steam **v1.4.6**；武器列表明确标注部分信息较旧。

| 来源 | 本轮使用内容 |
| --- | --- |
| [Items](https://neonabyss.fandom.com/wiki/Items) | 智慧之翼的 Boss 房间拾取条件、爆米花基本机制 |
| [Pets](https://neonabyss.fandom.com/wiki/Pets) | 宠物进化关系、光子合体关系 |
| [Weapons](https://neonabyss.fandom.com/wiki/Weapons) | 原版角色初始武器与名称；不使用列表中的旧总数作为当前版总数 |
| [Token](https://neonabyss.fandom.com/wiki/Token) | 神币及第八层入口关系 |
| [Level-?](https://neonabyss.fandom.com/wiki/Level-%3F) | 门票 1–4 的已记录获取渠道，以及各门票关联的特殊层玩法 |
| [Objects](https://neonabyss.fandom.com/wiki/Objects) | 街机损坏掉落 2 号门票；不采用同页未确认的 4 号门票扭蛋机来源 |
| [Item Sets](https://neonabyss.fandom.com/wiki/Item_Sets) | 四件套与钢铁意志的全部爆炸免疫 |
| [Keygun](https://neonabyss.fandom.com/wiki/Keygun) | 蓄力金钥匙的开锁目标和限制 |
| [R-6](https://neonabyss.fandom.com/wiki/R-6) | 猎户座是 R-6 的初始武器 |
| [Cooling System](https://neonabyss.fandom.com/wiki/Cooling_System) | 冰属性转换包括激光束 |
| [Danger Sign](https://neonabyss.fandom.com/wiki/Danger_Sign) | 电属性转换包括激光束 |
| [Agent Watch](https://neonabyss.fandom.com/wiki/Agent_Watch) | 伤害加成按当前钥匙数量计算 |
| [Golden Torch](https://neonabyss.fandom.com/wiki/Golden_Torch) | 新增道具房从后续层开始生效 |
| [Lidless Eye](https://neonabyss.fandom.com/wiki/Lidless_Eye) | 地图揭示不包括隐藏房间 |
| [Useless Item](https://neonabyss.fandom.com/wiki/Useless_Item) | 刷新方块能够重刷无用之物 |
| [Desert Elixir](https://neonabyss.fandom.com/wiki/Desert_Elixir) | 隐藏的体型/受击框/护盾/红心容器变化 |

## 已发现的版本差异与覆盖边界

- 本地版本提取结果为 v1.5.3.2，而外部 Wiki 主要是 v1.4.6；基础效果优先当前安装包，外部补充保留来源和适用边界。
- 本地多语言表包含两个简体中文版本。老大哥的中文数组索引 0 保留“免疫爆炸伤害”，索引 2 和英文描述明确为“免疫自身产生的爆炸伤害”；后者与 Veewo 调整记录一致。需要避免旧文案覆盖现行效果。
- Wiki `Upgrades` 顶部明确写信息过时，旧的逐道具天赋树成本和试用解锁方式未导入。
- 官网旧 FAQ 写神币多次神殿随机出现，Wiki 的 Token 页面给出不同的具体规则且页面未标版本。两种神币条目标注未实机核验，不把该页面规则冒称为明确 v1.4.6 或 v1.5.3.2 实测结果。
- 未找到能够核验全部道具限定掉落池的可信完整表；没有给普通条目伪造专属获取方式。
- 门票 5、6 和混沌门票只核验了作用，未核验特殊获取来源，故不添加特殊获取标记。
- 本地表中的新花生/宝系列与历史、不可获取条目需要结合游戏配置确认是否会在正常流程出现；本轮不根据语言表存在就宣称全部可获取。
- 老版 Steam Pipe 与当前本地命名无法精确对应，未强行对齐为铁狮。
- 所有文本补充和攻略均采用短篇中文概括，没有复制第三方长篇攻略。未下载第三方图标，因为本地资源提取成功。

## 最终当前配置对齐审查

已按提取完成的 `app/data/neon-abyss.entries.json` 核对。该文件共 **453** 条（311 道具、91 武器、51 宠物）；运行时补充已调整为 **43** 条，全部能按中文名或英文名匹配，零条残留失配。

三篇攻略涉及的老大哥、爆米花、钥匙枪、光子、曼哈顿、小皮皮、桔宝、曼小顿、小小皮、宝宝桔均仍有实际当前条目；没有使用被改为徽章的旧升级道具名称。老大哥正文已经按当前中文/英文说明统一为自身爆炸免疫。

以下三条从运行时补充删除，仅在这里保留调研边界：

- **智慧之翼 / Wings of Wisdom**：旧 Wiki v1.4.6 记载为雅典娜或诅咒雅典娜 Boss 房间的特殊拾取物；当前直接配置未以此名称匹配，因此没有据旧语言表重新注入当前词条。
- **仙人掌三代 / Cactus Baby III**：旧 Wiki 记录为仙人掌二代进化；本地相关配置标记 `isTestItem = 1`，当前百科提取流程排除。
- **熊猫 / Little Panda**：旧 Wiki 记录为熊仔进化；本地相关配置标记 `isTestItem = 1`，当前百科提取流程排除。

其他补充中的直接进化前阶、门票 2–4 的掉落来源明确标为 PC Wiki **v1.4.6 记录**；角色初始武器关系注明旧版来源。神币来源页面本身未标版本，已注明这一点与当前版本未实机核验，避免把不确定的次数标为新版本事实。

本地 `evolvesFrom` 字段不是直接前阶：例如亚当三代指向亚当一代、光子指向小小皮、孙悟空指向石头。字段只作系列起点参考，没有用它覆盖 Wiki 记载的直接进化关系。
