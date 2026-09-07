# 来源与声明差异

Verdict: `candidate_only`。本文件是来源核对，不是数学正确性回执。
检索日期：2026-09-06。仓库来源固定在 `bb001374124bc89a98c87cbffbb86aab32a01609`。

## 冻结源

- 仓库：vibemathing/problem-opg-1808-monochromatic-reachability
- ProblemContract：`problem-library/records/canonical-problems.jsonl`
- 合同声明摘要：`7ad1410069206a73b3cfd2149fc75d1509efc664f180b0ac96ae1f0f36473e8f`
- 义务：`research/records/obligation-graphs.jsonl`，`obligation:opg1808-directed-gallai-partition`
- 仓库失效历史：`research/records/failed-routes.jsonl`，读取时为空。
- 仓库 `research/artifacts` 路径在读取基线时返回404；不把该路径缺失误作准入记录缺失。
- 合同和 Harness 摘要本轮仅与声明值对照；没有声称重算整个 Harness。

## 原问题的公开题面

Open Problem Garden：
https://www.openproblemgarden.org/op/monochromatic_reachability_vs_rainbow_triangles

该页的主问题采用从一个顶点出发到各目标的单色有向路径，并只禁止三色有向三环。
这与本仓库的方向和三色调色板一致。该页另述更一般问题，不将它混入冻结合同。
来源地位：原题导航与声明对照；不是本轮反例候选的证明依赖。

## 无向 Gallai 定理

Anton Trygub, *Full Characterization of Color Degree Sequences in Complete Graphs Without Tricolored Triangles*，
arXiv:2304.14579v1（2023-04-28），Theorem 1.1：
https://arxiv.org/html/2304.14579v1

此处列出的 Gallai 定理针对没有任何无向彩虹三角形的完全图，保证块间单色及总体至多二色；
并没有统一弧方向的结论。与本轮分解断言的关系为 analogy，而不是 exact。
C01 显示前提差异；C02 显示即便补上该无向前提，方向结论仍无保证。
这里只作有界转述；没有复制论文。

## 容易混淆的“已证明”标题

N. Bousquet, W. Lochet, S. Thomassé, *A proof of the Erdős-Sands-Sauer-Woodrow conjecture*，
arXiv:1703.08123：
https://arxiv.org/abs/1703.08123

摘要的相关结论允许起点构成一个大小受颜色数控制的集合，而非要求一个起点。
因此该标题不能直接用作当前单顶点、禁止彩虹有向三环问题的解决证书。
本轮没有据此宣称冻结原题的现今解决状态。

## 出向/入向版本

Sarah Camille Mousley, *Tournament Directed Graphs*（2013），机构存档摘要：
https://digitalcommons.usu.edu/honors/652/

摘要采用各顶点到某汇点的路径版本。对于“所有 tournament”的命题，
全体弧反向在两个版本之间给出等价变换，并保持彩虹有向三环前提。
这不是声称一个固定 tournament 的同一顶点同时满足出向和入向版本。

## 需显式处理的基例

分解候选采用 n≥2，允许全单点分块。根问题的正向有限引理采用 n≥1。
合同的文字定义未单独说明空 tournament 的约定；正式编码前应由声明忠实性审查确认。
本轮全部分解障碍的阶数至少3，不依赖这一空对象约定。
不利用空对象歧义宣称原题被否定，也不改写合同。

## 证据边界

C01—C09 是本地批次给出的显式候选论证；不声称它们在文献中具有新颖性。
没有执行全体三至七顶点定向/着色的枚举，没有 Lean 构建，也没有生成任何验证器回执。


## 后续读取与不重复运输

本地准备期间，远端 main 已正常前进。循环开始时再次读取的实际基线为 `6294f75cd72274a4445576d5719fe347ed2f74f5`。
相对最初 `bb001374124bc89a98c87cbffbb86aab32a01609` 的已读 compare 只列出 candidate、
source-note、packet 路径新增，未列出合同、Harness、records 等控制文件的变化。

Issue #3 为已存在、开放且带 web-research-question 标签的唯一研究工单：
https://github.com/vibemathing/problem-opg-1808-monochromatic-reachability/issues/3 。

远端已经存在：
- `research/artifacts/candidates/opg1808-a01-c01-t3-20260906.md`：三顶点最小障碍；
- `research/artifacts/candidates/opg1808-a01-c02-t4-20260906.md`：另一种强连通四顶点着色；
- `research/artifacts/candidates/opg1808-a01-c03-family-20260906.md`：基于该着色的任意阶族。

这些对象在当前连接执行本地工作时被观察到；不能把它们的写入、PR 或 merge
说成本连接完成。旧 Issue #1 的预准入缺失仅为历史状态，不再作为当前阻断。

本地 C02/C03 的色表与远端 C02/C03 不同，保留是为了给有限检查器提供完整固定输入，
而不是把“强连通障碍”或“任意阶障碍”再包装为首次发现。
后续包的主要新增内容为 C05 的任意调色板四顶点等式分类、
C06 的三色五顶点排除、C07 的六七顶点精确编码与方向空间约束。

## 极小反例环的既有来源

Agelos Georgakopoulos and Philipp Sprüssel,
*On 3-coloured tournaments*, arXiv:0904.1967v2，2009-04-17：
https://arxiv.org/html/0904.1967v2 。

Lemma 2.1 在相同出向单色可达语义下给出特殊 Hamilton 环，并归于 Shen Minggang。
Lemma 2.7 给出相邻环弧不同色时的弦方向及反向可达第三色。
Theorem 3.1 进一步讨论极小反例每点的三色关联；本批次不把未逐项复核的该定理
用作 SAT 剪枝，也不把摘要关于局部双色子类的结论当作根命题的全范围结论。

C06 引入的每点入度/出度至少二与文中 Proposition 2.4 相容；
本地证明只处理度数一的特殊情况，完整标明最小性和整体反向的使用。
五顶点后续颜色排除为直接列出的有限推导，不宣称文献新颖性。

## 二色缩约和五顶点归结切片

C08 单独证明全图二色 tournament 的起点引理，并把它与 C04 的提升机制结合。
它只对显式递归定义的方向—颜色统一分块子类给出充分定理；不恢复已失败的普遍分解存在性。

C09 是 C06 正向弦分支的机器可读有限证明候选：
固定 q=(3,1,1,2,2) 后，把五个二元 p 域编码成五个布尔变量，
七条禁止单色短路给出七个子句；七步归结得到空子句。
这个文件没有经过程序检查，不是 solver 运行输出。
其适用范围不包含 C06 的前置最小性、度数、环和弦分类归约；
这些声明忠实性与依赖仍须另外验证。
