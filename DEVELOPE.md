# dongbei 开发人间指南

## 日常开发

dongbei 配了 CI（连续集成系统），确保项目体健貌端。
最新体检结果：[![体检结果](https://api.travis-ci.com/zhanyong-wan/dongbei.svg?branch=master)](https://travis-ci.com/zhanyong-wan/dongbei)。

提请 PR 前记得确定 CI 测试全部通过哦。
把测试搞坏了是要包赔的！

dongbei 采用业界领先的 TDD (TreeNewBee-Driven Development，学雷锋树新蜂) 方法开发。
基本上所有的 PR 都要包括吹牛逼（README.md 和 doc/cheatsheet.md）和测试案例（test/dongbei_test.py）。
不信？瞅瞅 commit 记录去。

## 新品发布

咱们用 PyPi 发布 dongbei 语言解释器命令行工具 `dongbei`。
CD 步骤都整好了！
欲发新版，项目经理只需依计行事：

（假设要发布版本 `x.y.z`）

1. 把根目录下 `setup.cfg` 文件里 `metadata` 项目内的 `version` 改成 `x.y.z`。
2. `git commit`
3. `git tag -a x.y.z` 把最新的 commit 标记成 `x.y.z`。
4. `git push --tags origin master` 把 commit 连同 tag 一起 push 到 GitHub repo；剩下的事交给 CD 就没毛病了！
