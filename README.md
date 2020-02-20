# dongbei - 东北方言编程语言

#### 体格咋地

[![体格咋地](https://api.travis-ci.com/zhanyong-wan/dongbei.svg?branch=master)](https://travis-ci.com/zhanyong-wan/dongbei)

扫码关注原作者微信公众号“老万故事会”
<img src="doc/lwgsh.jpg" height="129">

* [引言](#引言)
* [系统要求](#系统要求)
* [安装](#安装)
* [测试](#测试)
* [你好，世界](#你好世界)
* [学习材料](#学习材料)
* [跑程序](#跑程序)
* [参与开发](#参与开发)
* [周边](#周边)
  
## 引言

dongbei是啥？它是一门*以东北方言词汇为基本关键字的以人为本的编程语言。*

这玩意儿可是填补了世界方言编程地图上的一大片儿空地啊！
这么说吧，谁要是看了 dongbei 程序能憋住了不笑，我敬他是纯爷们儿！

那它有啥特点咧？多了去了：

*  简单啊！小学文化程度就行。您能看懂春晚不？能？那就没问题。
*  好读啊！看着看着包您不由自主地念出声儿来。
*  开心啊！呃，做人嘛，最重要的是要开心。
*  开源啊！不但不要钱，而且不要脸 -- 随时随地欢迎东北话高手打脸指正。

总而言之，dongbei 语言具有极高的**娱技比**（娱乐精神-技术含量比例）。

dongbei 编程语言的开发采用了业界领先的 **TDD（TreeNewBee-Driven Development）** 方式。
具体地说，就是每个功能都是先把文案写好，八字没一撇牛皮就吹起来了，然后根据牛皮写测试案例，最后再实现功能让牛皮不被吹破。
这样做有两大好处：第一每个功能都是有的放矢，不值得 tree new bee 的功能一概没有。
第二确保了每个功能都有文案负责吹嘘，开发者绝对不会养在深闺无人识。

不扯犊子了。翠花，上酸菜～～～

## 系统要求

dongbei 语言是基于 Python 3 二次开发的。
只要能跑 Python 3 的旮旯儿都能跑。
像 Mac OS 啦、Windows 啦、Linux 啦，等等等等，都成！

## 安装

用pip直接就能整上dongbei 。dongbei是Python3写的 ，建议使用pip3 。

```
# 给这台电脑的所有用户安装
pip3 install dongbei-lang

# 只给自己安装
pip3 install dongbei-lang --user

# 更新到最新的 dongbei 版本。要是只给当前用户更新，加 --user
pip3 install dongbei-lang --upgrade

# 使用
dongbei <xxx>.dongbei
```

要是你的系统没有pip3呢，也可以装一个，还是免费。详情可咨询：
[Windows](https://blog.csdn.net/menc15/article/details/65631380)
[Mac](https://blog.csdn.net/huangpin815/article/details/70194492)
[Ubuntu](https://www.jianshu.com/p/a0dd650dbd41)

当然你也可以直接跑 src/dongbei.py 。

要是你的系统没有python3呢，那得先装一个，免费！

比如，你要是用 Mac 的话，就按 [Mac Python3 安装指南](https://docs.python-guide.org/starting/install3/osx/) 做。

## 测试

没事跑跑
```
test/dongbei_test.py
```
身体更健康。

## 你好，世界

创建一个名字叫 hello-world.dongbei 的文本文件，内容如下：

```
唠唠：“唉呀，这嘎哒真他妈那啥！”。
```

用 utf-8 编码保存。
要是编辑器因为编码有毛病埋汰你，那就把文件内容改成

```
# -*- coding: utf-8 -*-

唠唠：“唉呀，这嘎哒真他妈那啥！”。
```

再试，应该就成了。

然后在命令行窗口运行：

```
dongbei hello-world.dongbei
```

你应该看到执行结果：

```
唉呀，这嘎哒真他妈那啥！
```

## 学习材料

要是你以前有 dongbei 语言基础，或者不耐烦看文档，可以直扑 [dongbei 语言考试小抄](doc/cheatsheet.md)。

要是你习惯以听歌的方式学习，请下载 dongbei 语言官方宣传歌曲[《Dongbei Style》](doc/Dongbei%20Style.mp3)（[歌词](doc/dongbei-style.md)）。

要是你想全面深入掌握 dongbei 语言，那就得读读 [dongbei语言咬文嚼字](doc/dongbei-ref.md)。

这里还有一些精选的示范程序供大家参考：

*  [快速排序](demo/快速排序.dongbei)

## 跑程序

目前人类已知的跑 dongbei 程序的方法有三种：

1. 要是没有用 pip3 安装 dongbei-lang，可以用 `src/dongbei.py 程序文件` 命令来跑一个 dongbei 程序。
2. 要是已经安装了 dongbei-lang，可以用 `dongbei 程序文件` 命令。
3. 要是已经安装了 dongbei-lang，也可以在一个 dongbei 程序文件的开头插入一行 `#!/usr/bin/env dongbei` 再把文件改成可执行的（比如在 Linux / Mac OS 上跑 `chmod +x 程序文件`）。然后，就可以直接用 `程序文件` 命令来跑码了。

用前两种方法的时候，可以在命令行加上 `--xudao`（絮叨）让系统打印和 dongbei 程序对应的 Python 代码。
这在开发和学习 dongbei 的时候大有裨益。

## 参与开发

dongbei 欢迎大伙儿帮衬。
要是您有意相助，请看[dongbei 开发人间指南](DEVELOPE.md)。

## 周边

一个好汉三个帮。
dongbei的老铁们开发了这些个周边项目，让你在用dongbei编程的时候如虎添翼，如鱼得水，如痴如醉，如胶似漆：

* VS Code 的 dongbei 语法高亮度插件：https://github.com/mingjun97/dongbei-vscode ，在插件商店[直接安装](https://marketplace.visualstudio.com/items?itemName=mingjun97.dongbei)就成。
* vim 的 dongbei 语法高亮度插件：https://github.com/suxpert/dongbei.vim ，整法自个儿瞅去。