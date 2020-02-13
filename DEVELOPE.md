# dongbei开发指南

## 开发
该项目已设置CI，提请PR前请先确定CI测试全部成功。

## 发布
`dongbei-lang`编译器命令行工具`dongbei`通过PyPi发布；CD步骤已经成功设置，项目管理人可以通过以下步骤自动化发布新版编译器。


假设即将发布版本`x.x.x`


1. 将根目录中`setup.cfg`中`metadata`项内的`version`改为`x.x.x`。
2. `git commit`当前修改。
3. `git tag -a x.x.x`将最新的commit标记为`x.x.x`。
4. `git push --tag origin master`将commit连同tag一起push到GitHub repo；CD将自动完成剩余发布任务。
