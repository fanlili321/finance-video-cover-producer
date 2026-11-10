# 本地清单与中断恢复

生成前建立任务目录，保存确认标题。helper 使用 Python 标准库，清单/hash/打包流式读取文件，不加载全部图片。图片标准化逐张使用 Pillow，macOS 没有 Pillow 时用 sips。

```bash
python3 scripts/delivery_manifest.py init --manifest '输出目录/交付清单.json' --titles '输出目录/确认标题.json' --ratios 9:16 4:3 16:9
```

标题输入支持字符串数组，或 `{ "selected": [{"title":"标题"}] }`。每个 title×ratio 为 pending。init 拒绝覆盖旧清单；默认三比例 N 个标题应有 3N 项。旧任务沿用其已有清单中的比例，续做时不自动增加 4:3 项。

先看原图，再标准化；随后看最终文件，逐字比对标题和标点、确认人物身份、无额外文字、构图不裁切，才能登记。accept 已验收且 hash 未变化的条目会拒绝重复登记；文件变化后须重新看图再登记：

```bash
python3 scripts/prepare_delivery.py '生成原图.png' --title '原标题' --ratio 9:16 --output-dir '输出目录'
python3 scripts/delivery_manifest.py accept --manifest '输出目录/交付清单.json' --title '原标题' --ratio 9:16 --file '输出目录/原标题 9-16.png' --visual-pass
python3 scripts/delivery_manifest.py check --manifest '输出目录/交付清单.json'
```

`--visual-pass` 是执行者实际看图验收的声明，脚本本身不识别文字/脸。不得为通过脚本而虚假勾选。accept 技术验证后记录相对文件名、大小、SHA256、验收时间。提示词、原图路径及失败原因可由 agent 另存生产日志，不保存飞书凭据。

check 会列出 pending/缺失/名称尺寸错误/hash变化；全部通过时输出唯一 upload allowlist。图片被替换后旧验收失效，必须重新看最终文件再 accept，不仅更新 hash。源图横竖方向不符或偏离目标比例超过 10% 时标准化拒绝，回到源图映射/生成阶段检查，不能强裁标题。

```bash
python3 scripts/delivery_manifest.py zip --manifest '输出目录/交付清单.json' --output '输出目录/视频封面.zip'
```

ZIP 只包含全量通过清单的独立 PNG，保留中文 UTF-8 文件名，不合并画布，不加清单/素材。已有 ZIP 拒绝覆盖，换新名字；PNG 无损，不用 JPEG 再压缩。

恢复步骤：读确认标题和清单 → check → 看缺失/失败项 → 逐张补齐；已验收且未变化的图不重做。并发只用于远端生图；工作线程不写清单，主流程逐项串行验收和登记。每个 title×ratio 使用唯一任务 ID 和独立临时目录。遇 429/usage_limit_reached 立即停派并记录断点；偶发超时只允许间隔后重试该图一次。上传恢复读飞书回执并核对远端，不能仅凭本地清单推断上传成功。用户若只要求上传，不重新生图。阶段间及时保存，可拆为“提取”“制作”“上传”三个独立请求。
