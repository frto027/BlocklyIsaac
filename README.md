# BlocklyIsaac
Create script for game The Binding of Isaac without lua.

[Try it](https://frto027.github.io/BlocklyIsaac/)

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

[Blockly](https://developers.google.com/blockly)


# 使用Blockly图形化编程创建游戏《以撒的结合》mod

游戏的接口定义在`game_blocks.js`文件中，该文件通过`CodeGenerator\class_parser.py`识别LuaDocs的doxygen文档自动生成。