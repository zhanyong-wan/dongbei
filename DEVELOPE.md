# dongbei 开发人间指南

## 方法论

dongbei 采用业界领先的 TDD (TreeNewBee-Driven Development，学雷锋树新蜂) 方法开发。
基本上所有的 PR 都要包括吹牛逼（README.md 和 doc/cheatsheet.md）和测试案例（test/dongbei_test.py）。
不信？瞅瞅 commit 记录去。

## 开发环境
一个好汉三个帮，dongbei 现在也用到了其他一些大哥大开发的工具来简化开发流程。开发 dongbei 之前请确定你的 coding 黑土地已经种上了所有我们需要的dependencies。

播种dependencies:
```bash
$ pip install -r requirements.txt 
```

## 连续集成

dongbei 用 travis-ci.com 做 CI（连续集成系统），确保项目体健貌端。
最新体检结果：[![体检结果](https://api.travis-ci.com/zhanyong-wan/dongbei.svg?branch=master)](https://travis-ci.com/zhanyong-wan/dongbei)。

提请 PR 前记得确定 CI 测试全部通过哦。
把测试搞坏了是要包赔的！

如果你需要修改 dongbei 的 CI 设置，有可能需要[安装 `travis` 命令行工具](https://github.com/travis-ci/travis.rb#installation)。
要是你没有自己机器的超级用户权限（比如，你的机器是公司统一管理的），安装的时候记得加上 `--user`，再把 `travis` 所在的路径加到你的 `PATH`。
举例说明：

1. `gem install travis -v 1.8.10 --no-rdoc --no-ri --user`
1. 在 `~/.profile` 中加上
   ```{shell}
   export PATH="$PATH:/Users/wangdada/.gem/ruby/2.3.0/bin"
   ```
   （假定你用 Mac 而且用户名是 `wangdada`）。

## 新品发布

咱们用 PyPi 发布 dongbei 语言解释器命令行工具 `dongbei`。
CD 步骤都整好了！
欲发新版，项目经理只需依计行事：

（假设要发布版本 `x.y.z`）

1. 把根目录下 `setup.cfg` 文件里 `metadata` 项目内的 `version` 改成 `x.y.z`。
1. 把 `src/dongbei.py` 文件里的 `DONGBEI_VERSION` 值改成 `x.y.z`。
1. 在根目录下的 `CHANGES.md` 文件里标注新版本有哪些变化。
1. `git commit -a -m "发布 x.y.z"`
1. `git tag -a x.y.z -m "发布 x.y.z"` 把最新的 commit 标记成 `x.y.z`。
1. `git push --tags origin master` 把 commit 连同 tag 一起 push 到 GitHub repo；剩下的事交给 CD 就没毛病了！
1. 要是不放心，喝二两小酒再到 https://pypi.org/project/dongbei-lang/#history 瞅瞅发布成功没。

记住，从 2021 年 8 月 13 日起 github 就要求在使用 git 命令行用 personal access token 而不是 github 口令来认证了。
详情请看[帮助](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)。