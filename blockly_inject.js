/*
MIT License

Copyright (c) 2020-2021 frto027

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

// Auto generated by python script
// var CallbackArguments = {
//   "MC_NPC_UPDATE":[
//     {name:"_",type:undefined},
//     {name:"EntityNPC",type:"EntityNPC"}
//   ],
// }
// var AddCallbackArguments = {
//   "MC_NPC_UPDATE":{
//     name:"EntityType",type:"EntityType"
//   },
//   "MC_USE_ITEM":{
//     name:"CollectibleType",type:"CollectibleType"
//   },
// }

//I HAVE TO rewrite it.
Blockly.Lua.ORDER_ATOMIC = 0;          // literals
// The next level was not explicit in documentation and inferred by Ellen.
Blockly.Lua.ORDER_HIGH = 1;            // Function calls, tables[]
Blockly.Lua.ORDER_EXPONENTIATION = 3;  // ^
Blockly.Lua.ORDER_UNARY = 4;           // not # - ~
Blockly.Lua.ORDER_MULTIPLICATIVE = 5;  // * / %
Blockly.Lua.ORDER_ADDITIVE = 6;        // + -
Blockly.Lua.ORDER_CONCATENATION = 11;   // ..
Blockly.Lua.ORDER_RELATIONAL = 12;      // < > <=  >= ~= ==
// 'and' 'or' order is wrong in lua, they shares the same order, but we dont use it
Blockly.Lua.ORDER_AND = 13;             // and
Blockly.Lua.ORDER_OR = 14;              // or
Blockly.Lua.ORDER_NONE = 99;

// The next level is inferred by ME
Blockly.Lua.ORDER_TABLE_ACCESS = 2

//补充完整Blockly的优先级定义
Blockly.Lua.ORDER_BIT_MOVE = 7  // << >>
Blockly.Lua.ORDER_BIT_AND = 8   // &
Blockly.Lua.ORDER_BIT_NOT = 9   // ~
Blockly.Lua.ORDER_BIT_OR = 10    // |

Blockly.Lua['tool_do'] = function(block) {
    var value_op = Blockly.Lua.valueToCode(block, 'op', Blockly.Lua.ORDER_NONE);
    var code = value_op + '\n';
    return code;
  };

Blockly.Lua['FunctionReturn'] = function(block){
  return 'return ' + Blockly.Lua.valueToCode(block, 'retvalue', Blockly.Lua.ORDER_NONE) + '\n'
}

Blockly.Lua['FlagTestExist'] = function(block){
  return [
    Blockly.Lua.valueToCode(block,'arg0',Blockly.Lua.ORDER_BIT_AND) + '&' + 
    Blockly.Lua.valueToCode(block,'arg1',Blockly.Lua.ORDER_BIT_AND) + '~=0' 
    ,Blockly.Lua.ORDER_RELATIONAL
  ]
}
Blockly.Lua['FlagAdd'] = function(block){
  return [
    Blockly.Lua.valueToCode(block,'arg0',Blockly.Lua.ORDER_BIT_OR) + '|' + 
    Blockly.Lua.valueToCode(block,'arg1',Blockly.Lua.ORDER_BIT_OR)
    ,Blockly.Lua.ORDER_BIT_OR
  ]
}
Blockly.Lua['FlagRemove'] = function(block){
  return [
    Blockly.Lua.valueToCode(block,'arg0',Blockly.Lua.ORDER_BIT_AND) + '&(~' + 
    Blockly.Lua.valueToCode(block,'arg1',Blockly.Lua.ORDER_BIT_NOT)+')'
    ,Blockly.Lua.ORDER_BIT_AND
  ]
}

//check type inject

var parent_of_block_type = {}
// type_alias have to a DAG
var type_aliase = {}

var type_dontcheck = ['Object', 'table']
var orig_check = Blockly.Connection.prototype.checkType

function compare_type_with_alias(a,b){
  while(type_aliase[a])
    a = type_aliase[a]
  while(type_aliase[b])
    b = type_aliase[b]
  return a == b
}
//note:it is not a true alias,
//a alias to b, c alias to b, then a.parent maybe b.parent, but a.parent can not be c.parent
//and b.parent can not be a.parent
function get_parent_with_alias(a){
  while(a){
    if(parent_of_block_type[a])
      return parent_of_block_type[a];
    a = type_aliase[a]
  }
}

function type_compat(a,b){
  //don't check
  if(type_dontcheck.indexOf(a) != -1 || type_dontcheck.indexOf(b) != -1)
    return true;
    
  //actually there is no boolean type in lua, everything can be boolean
  if(a == 'Boolean'){
    return true
  }
  //console.log(a)
  //console.log(b)
  if(a.indexOf('::')!=-1){
    let arr = a.split('::')
    a = arr[arr.length-1]
  }
  if(b.indexOf('::')!=-1){
    let arr = b.split('::')
    b = arr[arr.length-1]
  }
  while(b){
    if(compare_type_with_alias(a,b)){
      return true
    }
    b = parent_of_block_type[b]
  }
  //console.log("False")
  return false
}

Blockly.Connection.prototype.checkType = function(a){
  // console.log(this.check_)
  // console.log(a.check_)
  if(orig_check.call(this,a)){
    return true
  }
  let b
  if(this.type == Blockly.INPUT_VALUE && a.type ){
    b = a
    a = this
  }else{
    b = this
  }


  if(b.check_ && a.check_){
    if(type_compat(a.check_,b.check_)){
      return true //a string b string
    }
    for(let i=0;i<a.check_.length;i++){
      if(a.check_[i].length == 1){
        break
      }
      for(let j=0;j<b.check_.length;j++){
        if(b.check_[j].length == 1){
          break
        }
        if(type_compat(a.check_[i],b.check_[j]))
          return true //a array b array
      }
      if(type_compat(a.check_[i],b.check_))
        return true //a array b string
    }
    for(let j=0;j<b.check_.length;j++){
      if(b.check_[j].length == 1){
        break
      }
      if(type_compat(a.check_,b.check_[j]))
        return true //a string b array
    }
  }
  return false
}

Blockly.Lua['lambda_func'] = function(block) {
  var statements_stmt = Blockly.Lua.statementToCode(block, 'stmt');

  var arg_count = 0

  //find AddCallback -> ModCallbacks, get arg_count
  let blk = block
  while(blk) {
      if (blk.type == "Isaac::AddCallback" || blk.type == 'ModReference::AddCallback') {
        var callback_enum = blk.getInputTargetBlock("arg1")
        if(callback_enum && callback_enum.getFieldValue("ENUM_VAL")){
          var callback_type = callback_enum.getFieldValue("ENUM_VAL")
          if(callback_type && CallbackArguments[callback_type])
            arg_count = CallbackArguments[callback_type].length
        }
          break
      }
      blk = blk.getSurroundParent()
  }


  // TODO: Assemble Lua into code variable.
  var func = "function("
  for(let i=0;i<arg_count;i++){
    if(i > 0)
      func+=','
    func += '__arg_'+i
  }
  func += ')\n'
  var code =func + statements_stmt + "end ";
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Lua.ORDER_NONE];
};

// arguments
//delayed execute
function define_argument_blocks()
{
  var arr = []
  //define arguments blocks for each callback
  for(callback_name in CallbackArguments){
    for(let i=0;i<CallbackArguments[callback_name].length;i++){
      arr.push({
        "type": "CALLBACK_ARG_" + i + callback_name,
        "message0": translate_str(CallbackArguments[callback_name][i].name),
        "output": CallbackArguments[callback_name][i].type,
        "colour": 230,
        "tooltip": "",
        "helpUrl": ""
      })
      Blockly.Lua["CALLBACK_ARG_" + i + callback_name] = function(block){
        return ["__arg_" + i,Blockly.Lua.ORDER_ATOMIC]
      }
    }
  }
  Blockly.defineBlocksWithJsonArray(arr)
}
function updateChildArgumentBlocksWithCallback(callback_enum_str,block,this_is_addcallback = false){
  if(block == undefined){
    //I tried my best...
    return
  }
  //DFS
  if((block.type != "Isaac::AddCallback" &&  block.type != 'ModReference::AddCallback') || this_is_addcallback){
    let children = block.getChildren()
    //DFS all arguments
    for(let i=0;i<children.length;i++){
      //Do not parse next block
      if(children[i] == block.getNextBlock()){
        continue
      }
      updateChildArgumentBlocksWithCallback(callback_enum_str,children[i])
    }
  }
  //dfs next statement
  if(!this_is_addcallback && block.getNextBlock()){
    updateChildArgumentBlocksWithCallback(callback_enum_str,block.getNextBlock())
  }
  if(block.type.startsWith("CALLBACK_ARG_")){
    // console.log("Update me:" + block.type)
    if(callback_enum_str){
      if(block.type.endsWith(callback_enum_str)){
        block.setWarningText()
      }else{
        block.setWarningText(translate_str("%{ARGUMENT_POS_ERROR}"))
      }
    }else{
      block.setWarningText(translate_str("%{ARGUMENT_IS_UNLINKED}"))
    }
  }
}
function handlerCallbackArgBlockWarring(evt){
  function find_add_callback(blkid){
    if(blkid){
      var blk = Code.workspace.getBlockById(blkid)
      while(blk && (blk.type != "Isaac::AddCallback"  && blk.type != 'ModReference::AddCallback')){
        blk = blk.getParent()
      }
      return blk
    }
    return undefined
  }
  function getCallbackEnum(addcallback){
    if(addcallback){
      var callback_enum = addcallback.getInputTargetBlock("arg1")
      if(callback_enum && callback_enum.getFieldValue("ENUM_VAL")){
        return callback_enum.getFieldValue("ENUM_VAL")
      }
    }
    return undefined
  }

  if(evt.type == Blockly.Events.MOVE && evt.oldParentId != evt.newParentId){
    let old_addcallback = find_add_callback(evt.oldParentId)
    let new_addcallback = find_add_callback(evt.newParentId)
    if(old_addcallback != new_addcallback){
      var newenum = getCallbackEnum(new_addcallback)
      var oldenum = getCallbackEnum(old_addcallback)
      if(newenum != oldenum){
        //drag argument from AddCallback A to AddCallback B
        updateChildArgumentBlocksWithCallback(newenum,Code.workspace.getBlockById(evt.blockId))
      }
    }
  }else if(evt.type == Blockly.Events.CHANGE){
    let target = Code.workspace.getBlockById(evt.blockId)
    if(target){
      if(target.type == "ModCallbacks" && evt.name == "ENUM_VAL" && evt.newValue && evt.newValue != evt.oldValue){
        //当ModCallbacks枚举变量改变时
        while(target && (target.type != "Isaac::AddCallback" && target.type != "ModReference::AddCallback")){
          target = target.getParent()
        }
        //更新所有的Argument
        if(target){
          updateChildArgumentBlocksWithCallback(evt.newValue,target,true)
        }
      }
    }
  }
}

var arg_config = {}

function defineArgumentCategory(){
  let categorys = {}
  for(callback_name in CallbackArguments){
    let cat_str = "<xml>"
    for(let i=0;i<CallbackArguments[callback_name].length;i++){
      cat_str += "<block type='"+ "CALLBACK_ARG_" + i + callback_name +"'></block>"
    }
    cat_str += "</xml>"
    let cat_str_nodes = Blockly.Xml.textToDom(cat_str).childNodes
    let cat_str_arr = []
    for(let i=0;i<cat_str_nodes.length;i++){
      if(i == 0){
        //ignore this
        continue
      }
      cat_str_arr.push(cat_str_nodes[i])
    }
    categorys[callback_name] = cat_str_arr
  }

  Code.workspace.registerToolboxCategoryCallback('Arguments',()=>{
    if(categorys[arg_config.last_type]){
      return categorys[arg_config.last_type]
    }
    return []
  })
}
function handleAddCallbackSelect(blk){
  arg_config.last_select_id = blk.id
  //Assert blk is AddCallback
  //find arguments
  var callback_enum = blk.getInputTargetBlock("arg1")
  if(callback_enum && callback_enum.getFieldValue("ENUM_VAL")){
    var callback_type = callback_enum.getFieldValue("ENUM_VAL")
    if(arg_config.last_type != callback_type){
      //Set arguments
      arg_config.last_type = callback_type
    }
    //AddCallback last argument
    if(AddCallbackArguments[callback_type]){
      blk.getInput('arg3').fieldRow[0].setValue(translate_str(AddCallbackArguments[callback_type].name))
      blk.getInput('arg3').setCheck([AddCallbackArguments[callback_type].type])
    }else{
      blk.getInput('arg3').fieldRow[0].setValue(translate_str("%{NOT_USED}"))
    }
  }
}


function handleAddCallbackDelete(evt){
  if(evt.ids.indexOf(arg_config.last_select_id) >= 0){
    arg_config.last_type = ""
  }
}

function handleArgumentChangeSelect(evt){
  let target_block = undefined
  if(evt.type == Blockly.Events.CHANGE){
    let target = Code.workspace.getBlockById(evt.blockId)
    if(target){
      if(target.type == "ModCallbacks" && evt.name == "ENUM_VAL" && evt.newValue && evt.newValue != evt.oldValue){
        //当ModCallbacks枚举变量改变时
        target_block = target
        while(target_block && (target_block.type != "Isaac::AddCallback" && target_block.type != "ModReference::AddCallback" )){
          target_block = target_block.getParent()
        }
      }
    }
  }else if(evt.type == Blockly.Events.CREATE){
    //当AddCallback创建时
    let target = Code.workspace.getBlockById(evt.blockId)
    if(target && (target.type == "Isaac::AddCallback" || target.type == "ModReference::AddCallback"))
      target_block = target
  }else if(evt.type == Blockly.Events.UI && evt.element=="click"){
    //当点击AddCallback时
    let target = Code.workspace.getBlockById(evt.blockId)
    if(target && (target.type == "Isaac::AddCallback" || target.type == "ModReference::AddCallback"))
      target_block = target
  }
  if(target_block){
    handleAddCallbackSelect(target_block)
  }

  if(evt.type == Blockly.Events.DELETE){
    handleAddCallbackDelete(evt)
  }
}
function setup_callback_graph(){
  let mod_callback_blockdef = Blockly.Blocks["ModCallbacks"]
  mod_callback_blockdef.customContextMenu = (menuitems)=>{
    menuitems.push({
      text:translate_str("%{CALLBACK_GRAPH}"),
      enabled:true,
      callback:()=>{
        window.open(translate_str("%{CALLBACK_GRAPH_PATH}"))
      }
    })
  }
}

function replaceFunc(block,func){
  let v = block.init
  block.init = function(){
    v.call(this)
    func.call(this)
  }
}

function getRandStr(){
  var str = "abcdefghijklmnopqrstuvwxyz0123456789"
  var rand = Math.floor(Math.random()*1000000000)

  var r = ""
  while(rand > 0){
    r += str[rand % str.length]
    rand = Math.floor(rand / str.length)
  }
  return r
}

var ToolButtonOperations = {
  open:function(){
    document.getElementById('open_file_dialog').click()
  },
  save:function(){
    var save_file_href = document.getElementById("save_file_href")
    var xml = Blockly.Xml.workspaceToDom(Code.workspace);
    var text = Blockly.Xml.domToText(xml);
    save_file_href.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    save_file_href.setAttribute('download', 'output_' + getRandStr() +'.biml');
    save_file_href.click()
  },
  save_as:function(){

  },
  exportlua:function(){
    var save_file_href = document.getElementById("save_file_href")
    var luacode = Blockly.Lua.workspaceToCode(Code.workspace)
    save_file_href.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(luacode));
    save_file_href.setAttribute('download', 'main.lua');
    save_file_href.click()
  }
}

//called after workspace init
function inject_init(){
  //hide switch labels
  if(Code.getStringParamFromUrl('dev') != '1'){
    let hides = document.getElementsByClassName('normal_hide')
    for(let i=0;i<hides.length;i++){
      hides[i].hidden = true
      hides[i].style.display='none'
    }
    document.getElementById('btn_panel').style.textAlign = 'left' 
  }

  Blockly.defineBlocksWithJsonArray(translate_tjson([{
      "type": "registermod",
      "message0": "%{MODNAME} %1",
      "args0": [
        {
          "type": "input_value",
          "name": "TEXT",
          "check": "String"
        }
      ],
      "inputsInline": true,
      "output": "table",
      "colour": 230,
      "tooltip": "%{MOD_NAME_TOOLTIP}",
      "helpUrl": ""
    },{
      "type": "tool_do",
      "message0": "%{DO} %1",
      "args0": [
        {
          "type": "input_value",
          "name": "op"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": 230,
      "tooltip": "%{TOOL_DO_TOOLTIP}",
      "helpUrl": ""
  },{
    "type": "lambda_func",
    "message0": "%{FN_REF} %1",
    "args0": [
      {
        "type": "input_statement",
        "name": "stmt"
      }
    ],
    "output": "function",
    "colour": 230,
    "tooltip": "%{FN_REF_TOOLTIP}",
    "helpUrl": ""
  },{
    "type":"FunctionReturn",
    "message0":"%{FN_RET_VALUE} %1",
    "args0":[
      {"type":"input_value","name":"retvalue",align:"RIGHT"}
    ],
    "previousStatement": null,
    "colour":230,
    "tooltip":"%{FN_RET_TOOLTIP}"
  },{
    "type":"FlagTestExist",
    "message0":"[%{__TYPE_BOOL}]%{FLAG_CALLED}[%{__TYPE_INTEGER}]%1%{FLAG_CONTAINS}[%{__TYPE_INTEGER}]%2",
    "args0":[
      {"type":"input_value","name":"arg0","check":"integer",align:"RIGHT"},
      {"type":"input_value","name":"arg1","check":"integer",align:"RIGHT"},
    ],
    "output": "boolean",
    "colour": 230,
    "inputsInline":true,
    "tooltip":"%{FLAT_TEST_EXIST_TOOLTIP}"
  },{
    "type":"FlagAdd",
    "message0":"[%{__TYPE_INTEGER}]%{FLAG_CALLED}[%{__TYPE_INTEGER}]%1%{FLAG_ADD}[%{__TYPE_INTEGER}]%2",
    "args0":[
      {"type":"input_value","name":"arg0","check":"integer",align:"RIGHT"},
      {"type":"input_value","name":"arg1","check":"integer",align:"RIGHT"},
    ],
    "output": "integer",
    "colour": 230,
    "inputsInline":true,
    "tooltip":"%{FLAT_TEST_ADD_TOOLTIP}"
  },{
    "type":"FlagRemove",
    "message0":"[%{__TYPE_INTEGER}]%{FLAG_CALLED}[%{__TYPE_INTEGER}]%1%{FLAG_REMOVE}[%{__TYPE_INTEGER}]%2",
    "args0":[
      {"type":"input_value","name":"arg0","check":"integer",align:"RIGHT"},
      {"type":"input_value","name":"arg1","check":"integer",align:"RIGHT"},
    ],
    "output": "integer",
    "colour": 230,
    "inputsInline":true,
    "tooltip":"%{FLAT_TEST_REMOVE_TOOLTIP}"
  }]))
  define_argument_blocks()


  init_game_blocks()
  setup_callback_graph()
  //Arguments
  defineArgumentCategory()
  
  //Change callback argument names
  Code.workspace.addChangeListener(handleArgumentChangeSelect)
  Code.workspace.addChangeListener(handlerCallbackArgBlockWarring)
  // replaceFunc(Blockly.Blocks["Isaac::AddCallback"],function(){
  //
  // })
  document.getElementById('copy_to_console').title = translate_str('%{COPY_TO_CONSOLE_BTN_TEXT}')
  document.getElementById('copy_to_console_electron').title = translate_str('%{COPY_TO_CONSOLE_BTN_TEXT}')
  new ClipboardJS('#copy_to_console',{text:function(trigger){
    let comment_func = Blockly.Block.prototype.getCommentText
    Blockly.Block.prototype.getCommentText = ()=>null
    let txt = Blockly.Lua.workspaceToCode(Code.workspace)
    Blockly.Block.prototype.getCommentText = comment_func
    txt = txt.replaceAll(/\n */g,'\n')
    txt = txt.replaceAll('\n',';')
    return 'l ' + txt
  }}).on('success',function(){
    Blockly.alert(translate_str("%{COPY_SUCCESS}"))
  })

  var open_btn = document.getElementById('open_file')
  var open_file_dialog = document.getElementById('open_file_dialog')
  open_btn.title = translate_str('%{OPEN_FILE_BTN_TEXT}')
  Code.bindClick(open_btn ,function(){
    ToolButtonOperations.open()
  })
  open_file_dialog.addEventListener('change',function(){
    if(open_file_dialog.files.length == 0){
      return;
    }
    var file = open_file_dialog.files[0];
    open_file_dialog.value = ''
    file.text().then(text=>{
      var xml = Blockly.Xml.textToDom(text)
      Code.workspace.clear()
      Code.workspace.clearUndo()
      Blockly.Xml.domToWorkspace(xml, Code.workspace)
    })
  })

  var save_btn = document.getElementById("save_file")
  
  save_btn.title = translate_str('%{SAVE_FILE_BTN_TEXT}')
  Code.bindClick(save_btn,function(){
    ToolButtonOperations.save()
  })

  var save_as_btn = document.getElementById('save_file_as')
  save_as_btn.title = translate_str('%{SAVE_FILE_AS_BTN_TEXT}')
  Code.bindClick(save_as_btn,function(){
    ToolButtonOperations.save_as()
  })

  var export_lua_btn = document.getElementById("export_lua")
  export_lua_btn.title = translate_str('%{EXPORT_LUA_BTN_TEXT}')
  Code.bindClick(export_lua_btn,function(){
    ToolButtonOperations.exportlua()
  })

  var undo_btn = document.getElementById("undo")
  undo_btn.title = translate_str('%{UNDO}')
  Code.bindClick(undo_btn,function(){
    Code.workspace.undo()
  })

  var new_window_btn = document.getElementById('new_window_button')
  new_window_btn.title = translate_str('%{NEW_WINDOW_BTN_TEXT}')
  document.title = translate_str('%{WEB_PAGE_TITLE}')

  var download_offline_btn = document.getElementById('download_offline')
  download_offline_btn.title = translate_str('%{DOWNLOAD_OFFLINE_TOOLTIP}')
  Code.bindClick(download_offline_btn,function(){
    if(window.location.href.indexOf('gitee.io') != -1){
      //gitee release page
      window.open('https://gitee.com/frto027/BlocklyIsaac/releases')
    }else{
      //github releasee page
      window.open('https://github.com/frto027/BlocklyIsaac/releases')
    }
  })

  var help_btn = document.getElementById('helpButton')
  help_btn.title = translate_str('%{HELP_BUTTON_TOOLTIP}')
  document.getElementById('helpButton_electron').title = translate_str('%{HELP_BUTTON_TOOLTIP}')
  Code.bindClick(help_btn,function(){
    window.open('bi-docs/bi-docs-cn/site/')
  })
  var copyright_btn = document.getElementById('copyright_btn')
  var copyright_span = document.getElementById('copyright_span')
  copyright_span.innerText = translate_str('%{COPYRIGHT}')
  Code.bindClick(copyright_btn,function(){
    alert(`
MIT License

Copyright (c) 2020-2021 frto027

BlocklyIsaac project page: 
https://github.com/frto027/BlocklyIsaac

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
    `)
  })
  
  try{
    electron_inject_init()
  }catch(e){ }
}

//translate
var trans_reg = /%{([A-Z0-9:_]+)}/g

function translate_str(str){
  return str.replace(/%{([A-Z0-9:_]*)}/g,(m,a)=>{
    //console.log(a)
    if(TMSG[a]){
      return TMSG[a]
    }
    return m
  })
}
function translate_tjson(json){
  for(k of json){
    k.message0 = translate_str(k.message0)
    k.tooltip = translate_str(k.tooltip)
    if(k.args0 && k.args0.length > 0 && k.args0[0].name=="ENUM_VAL"){
      var opts = k.args0[0].options
      for(let i=0;i<opts.length;i++){
        opts[i][0] = translate_str(opts[i][0])
      }
    }
  }
  return json
}

function get_blk_help(url){
  return "https://moddingofisaac.com/docs/rep" + url
}

