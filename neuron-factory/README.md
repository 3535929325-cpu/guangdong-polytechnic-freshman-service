# 神经元工厂 · 单词记忆连接片

75 秒、16:9 代码驱动叙事视频。Blender Python 出成片，Three.js 同源预览对轨。

## 快速开始（Three.js 预览）

```bash
cd neuron-factory/web
npm install
npm run dev
```

打开本地地址，点 Play 即可按 `shared/storyboard.json` 播放整条故事。

导出备份 MP4（无 Blender 时）：

```bash
npm run capture
```

## Blender 成片

需安装 Blender 3.6+：

```bash
cd neuron-factory
blender --background --python blender/scripts/01_build_assets.py
blender --background --python blender/scripts/02_animate_story.py
blender --background --python blender/scripts/03_render_eevee.py
```

输出：`exports/final/neuron_factory.mp4`

## 真相源

所有镜号、字幕、事件以 [`shared/storyboard.json`](shared/storyboard.json) 为准。
