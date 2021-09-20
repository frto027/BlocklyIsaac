# 如何创建一个指向biml文件的链接

可以在指向index.html的链接中，通过`biml_url`参数指令biml文件的路径。

比如[点我打开](../../../index.html?lang=zh-hans&biml_url=bi-docs/bi-docs-cn/site/bimls/HurtBigger_DieSpawn.biml)。

但是，你还可以用另外一种方式来实现：

<span b-url="bi-docs/bi-docs-cn/site/bimls/HurtBigger_DieSpawn.biml" />

文件的路径必须是相对于编辑器主页`index.html`所在目录的路径。编辑器会去下载这个文件，因此请确保同源策略不会出问题。
