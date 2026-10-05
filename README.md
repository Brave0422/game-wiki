# 游戏百科

PC 端游戏资料站，收录《霓虹深渊》的道具、武器、宠物与角色，以及《哈迪斯》的祝福与武器。采用 Nuxt 4、Vue 3、TypeScript、SCSS 和 Lucide 图标，关闭服务端渲染，浏览器直接读取项目中的本地数据，无需数据库或后端服务。

## 本地运行

需要 Node.js 22.19+ 或 24.11+，项目开发环境为 Node.js 24。

```sh
npm install
npm run dev
```

访问 <http://127.0.0.1:3000>。类型检查使用 `npm run typecheck`。

图鉴和图片完整性检查使用 `npm run check:data`。

## 当前功能

- 游戏库首页提供游戏封面、中英文搜索与收录状态筛选，霓虹深渊和哈迪斯可进入专区；饥荒、文明 VI 标为待收录。
- 霓虹深渊提供百科和攻略；百科内提供道具、武器、宠物、角色分类，角色分类紧随宠物。
- 哈迪斯提供祝福与武器导航，祝福包含作用和前置获取条件；六种武器提供全部二十四种形态的 I–V 级效果、每级属性增量和泰坦之血消耗。
- 名称/英文名/效果搜索、效果标签、特殊获取筛选、名称排序、卡片/列表切换与加载更多。
- 词条详情展示完整作用、武器附带技能、宠物形态说明、角色初始属性、获取条件与参考链接；详情链接可直接打开和分享。
- 本地收藏、深浅主题和 `Ctrl/Cmd + K` 搜索快捷键。
- 三篇机制与搭配攻略；霓虹深渊没有模组栏目，原模组地址返回未找到页面。

## 静态构建

```sh
npm run generate
npm run preview
```

将 `.output/public/` 部署到静态托管即可。首页及已开放游戏的各栏目生成独立 HTML 入口，也提供 `200.html` / `404.html` 回退。当前生成游戏库首页、霓虹深渊百科与攻略、哈迪斯祝福与武器入口。预览与开发共用 3000 端口，切换前先停止原服务。

游戏目录维护在 `app/constants/games.ts`：各游戏的 `sections` 决定导航顺序和默认入口，栏目 ID 不限制为百科、攻略、模组。新增游戏时配置所需栏目并实现对应页面，静态构建会读取已开放游戏的栏目路由。待收录游戏没有可点击的专区入口。

## 内容与资源

- `app/data/` 保存图鉴的本地数据；修改数据后重新构建即可更新网站。
- `public/` 保存静态图标和图片，页面运行时无需读取本机 Steam 安装目录。
- 首页游戏封面来自各游戏的官方 Steam 店面：[饥荒](https://store.steampowered.com/app/219740/)、[文明 VI](https://store.steampowered.com/app/289070/)、[哈迪斯](https://store.steampowered.com/app/1145360/)及[霓虹深渊](https://store.steampowered.com/app/788100/)，均保存在项目中并从本站加载。
- 资料来源及版本范围以站内来源说明为准。游戏图像和名称归各自权利人所有。
- 本期使用结构化 JSON 查询资料，暂未引入 Nuxt Content；需要 Markdown 攻略文章时可再接入。

图鉴按用户提供的 Steam PC **1.5.3.2 / build 20190109** 实际配置整理：311 件道具、91 种武器和 51 种宠物形态，共 453 条。不同名称的进化形态分别收录，相同显示名称的配置副本合并。64 种武器附带技能作用与消耗说明。

`neon-abyss.entries.json` 为本地原始图文；`neon-abyss.supplements.json` 保存 43 条网上核对的获取/进化补充；`neon-abyss.guides.json` 保存攻略。页面在浏览器中合并这些数据。`neon-abyss.source.json` 记录配置、图标对应关系和提取限制，`research/neon-abyss-sources.md` 记录外部资料出处与版本差异。

条目来自非测试配置，但没有逐项进入游戏验证所有模式的掉落。网上获取条件存在旧版来源，相关版本范围在词条中注明；武器射击图的内部数值未转换成数值表。游戏资源提取脚本为 `scripts/extract-neon-abyss.py`，网站正常运行不需要 Python 或原始游戏文件。

霓虹深渊新增 21 个角色条目（11 个基础角色、10 个异装），共 474 条。`neon-abyss.characters.json` 保存头像、初始生命容器/护盾/钥匙/手雷/金币、初始武器和角色特性；`neon-abyss.characters.source.json` 保存实际配置与图标引用。可用 `scripts/extract-neon-abyss-characters.py` 从本地安装重新提取。

哈迪斯共 172 个祝福、6 把武器，24 种形态合计 120 行升级数据。`hades.entries.json` 保存可展示的图文；`hades.source.json` 记录配置文件摘要、祝福前置关系、形态属性引用与图集裁剪坐标。图片均从本地游戏 GUI 图集按实际动画引用提取；运行网站不需要 Steam 安装。提取脚本为 `scripts/extract-hades.py`，依赖 `pillow`、`lz4`、`sjson`、`lupa` 和 [deppth](https://github.com/quaerus/deppth)。来源说明见 `research/hades-sources.md`。
