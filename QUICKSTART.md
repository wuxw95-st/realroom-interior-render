# Quick Start（给不看代码的用户）

## 你以后怎么用

你只需要准备：

1. 房间实拍图
2. 可选：参考设计图 / 家具图
3. 一句话要求，例如：
   - “只把床顺时针转90度，其他都别动”
   - “把图1的白色衣柜放到图2右侧墙，衣柜1.24×2×0.6m，墙长3.12m”
   - “只换木地板，给4种方案，分别输出，不要合并”

系统会把这些要求转换成 RealRoom 请求并执行。

## 第一次安装

前提：电脑上已经有可运行的 ComfyUI。

在终端进入本仓库后运行：

```bash
COMFYUI_DIR=/你的/ComfyUI路径 bash scripts/install.sh
```

然后按照 `docs/MODELS.md` 放好模型文件，并重启 ComfyUI。

## 测试规则是否解析正确

```bash
python3 scripts/realroom.py examples/request-schema.yaml --dry-run
```

这一步不会生成图片，只会检查请求和自动生成的约束参数。

## 真正生成

当完整 API workflow 准备好后：

```bash
python3 scripts/realroom.py your-request.yaml \
  --workflow workflow/realroom-production-api.json \
  --server http://127.0.0.1:8188
```

## 最重要的默认规则

- 墙、门、窗、天花、拍摄角度默认锁定。
- 没让改的家具默认锁定。
- “只改X” = 只允许 X 变化。
- 多角度必须分别输出，不自动拼图。
- 第二个角度继续用第二张原始实拍图，不用第一张渲染图重画空间。
- 生成结果如果改了墙体、角度、家具方向或尺寸明显不对，应判失败重做。

## 当前状态

v1 已包含：

- Skill 规则
- 默认控制参数
- 请求格式
- ComfyUI 安装脚本
- ComfyUI API runner
- workflow 绑定模板
- 渲染验收清单

还需要在目标电脑的 ComfyUI 中导出一份完整的 API workflow 并完成节点绑定，才能实际出图。这个步骤和你机器上安装的 ComfyUI/节点/模型版本有关，因此不能仅靠 GitHub 静态文件保证完全一致。
