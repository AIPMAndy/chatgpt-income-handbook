# v2.2 发布与对抗式验收记录（2026-10-22）

本报告纠正此前错误引用旧版章节数量和仓库建立状态的问题。**以 GitHub Actions 对应提交的执行结果为事实依据**；不把上传代码等同于实际在线访问验收。

## 已确认的项目基线
- 公开仓库 AIPMAndy/chatgpt-income-handbook 已经存在并启用了 GitHub Pages，上一版本有成功部署记录。
- 原始基线有 45 个文件；内容为 **34 章**、10 个服务包、**64 套**提示词、**36 个**FAQ、4个模拟案例和13个官方链接。
- 本次引入独立计算模块、Node负面测试、证据公开判断、完整模拟试单和修正后的事实台账。
- GitHub发布门禁包含 Python、JS 语法和 Node 算术情景测试。**必须查阅最新运行记录，不可预先宣布成功。**

## 尚未实际测试 / 不可宣传的内容
- 本次未实际测试所有正式网址、浏览器设备的线上交互；在发布后需再核查。
- 没有真实付款、真实客户签收或税务审核的完整证据。
- 没有经第三方独立确认的全网覆盖率比较，不得声称“全网第一”。
- 没有独立统计10种服务的市场价格、成交概率或真实利润分布。
- 模拟案例和作者自述不能用作收入承诺。

## 发布检查
1. [内容与算术测试](https://github.com/AIPMAndy/chatgpt-income-handbook/actions/workflows/check.yml) Success。
2. [网站部署](https://github.com/AIPMAndy/chatgpt-income-handbook/actions/workflows/deploy-pages.yml) 与最新提交一致并成功。
3. 打开 https://aipmandy.github.io/chatgpt-income-handbook/ 检查手机/桌面、官网与微信 AIPMAndy、章节检索、计算器及案例证据检查。
4. 检查零单、100%退款、负数、人工时间价值与正现金预留等情景。
5. 用 [完整模拟试单](END-TO-END-TRIAL.md) 核对需求、授权、变更、交付及验收标准。
