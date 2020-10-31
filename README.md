
# 使用Blockly图形化编程创建游戏《以撒的结合》mod

这个工程允许你使用Google Blockly图形化编程语言来创建游戏的mod。你可以在[点击此处](http://frto027.gitee.io/blocklyisaac/?lang=zh-hans)进行试用。

游戏的接口定义在`game_blocks.js`文件中，该文件通过`CodeGenerator\class_parser.py`识别LuaDocs的doxygen文档自动生成。


# BlocklyIsaac
Create script for game The Binding of Isaac without lua.

[Try it at git page](https://frto027.github.io/BlocklyIsaac/)

[Try it at gitee page](http://frto027.gitee.io/blocklyisaac/)

You can create script like:

![img](CodeGenerator/2020-08-04-20_54_24.jpg)

Then you can get the following script by clicking on the Lua tab.

```lua
MyMode = RegisterMod('ModName',1)
Isaac.AddCallback(MyMode,ModCallbacks.MC_USE_ITEM,function(__arg_0,__arg_1,__arg_2)
  if (Isaac.GetPlayer(0)):GetSoulHearts() / 2 > 3 then
    (Game()):BombDamage((Isaac.GetPlayer(0)).Position,1,1,true,Isaac.GetPlayer(0),0,0,true)
  end
end ,CollectibleType.COLLECTIBLE_D20)
```

# Reference

[Blockly](https://developers.google.com/blockly)

[IsaacDocs](https://github.com/wofsauge/IsaacDocs)


# How to build

the project is already built, you can click `index.html` to run directly.

However, if you want to build it yourself, you can run the folowing command with `python 3`.

> Please make sure that the git submodule `IsaacDoc` has been initialized before building. The API and translation files are automatically generated based on the doxygen documentation in that project.

```
git clone https://github.com/frto027/BlocklyIsaac.git
cd BlocklyIsaac
git submodule init
git submodule update
python -m pip install bs4

python ./CodeGenerator/class_parser.py
```


# Translate it to your language

1. Uncomment the `Code.LANGUAGE_NAME` variable in the `code.js`.
2. Add an item to the `translate_files` variable in `CodeGenerator/class_parser.py`
3. Rebuild project.
4. Edit your language config at `code_translate` directory.
