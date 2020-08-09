/*
MIT License

Copyright (c) 2020 frto027

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



Blockly.Lua['registermod'] = function(block) {
    var value_text = Blockly.Lua.valueToCode(block, 'TEXT', Blockly.Lua.ORDER_ATOMIC);
    var code = 'RegisterMod('+value_text+',1)';
    return [code, Blockly.Lua.ORDER_NONE];
};
Blockly.Lua['tool_do'] = function(block) {
    var value_op = Blockly.Lua.valueToCode(block, 'op', Blockly.Lua.ORDER_NONE);
    var code = value_op + '\n';
    return code;
  };


//check type inject

var parent_of_block_type = {}

var orig_check = Blockly.Connection.prototype.checkType

function type_compat(a,b){
  //console.log(a)
  //console.log(b)
  while(b){
    if(a==b){
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
      if (blk.type == "Isaac::AddCallback") {
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


var DEBUGGER = false
// arguments
var arg_config = {arg_mxcount: 10}
//delayed execute
function define_argument_blocks()
{
  var arg_mxcount = arg_config.arg_mxcount
  var arr = []
  for(let i=0;i<arg_mxcount;i++){
    arr.push({
      "type": "FUNC_ARG_"+i,
      "message0": "arg "+i,
      "output": "Boolean",
      "colour": 230,
      "tooltip": "",
      "helpUrl": ""
    })
    Blockly.Lua["FUNC_ARG_"+i] = function(block){
      return ["__arg_" + i,Blockly.Lua.ORDER_NONE]
    }
  }
  Blockly.defineBlocksWithJsonArray(arr)

  for(let i=0;i<arg_mxcount;i++){
    Blockly.Blocks['FUNC_ARG_'+i].onchange = function(evt){
      //优先处理自身的blk
      //只处理移动
      console.log(evt)
      if(evt.type != 'move' && evt.type != 'ui'){
        return
      }

      if(evt.type == 'ui'){
        if(!((evt.element=='click' ||evt.element=="dragStart")&& evt.blockId == this.id)){
          return
        }
        return
      }

      if(this.stick_block != undefined){
        return
        if(evt.newParentId == undefined)
          return
        //是否是自己的parent移动了，不是的话别管
        {
            let blk = this
            
            while(blk && blk.id != evt.blockId){
              blk = blk.getParent()
            }
            if(!blk){
              return
            }
        }
      }

      let blk = this
      while(blk && blk.type != 'Isaac::AddCallback'){
        blk = blk.getParent()
      }

      let target_argument = undefined 
      if(blk){
        //change it to parent argument names
        var callback_enum = blk.getInputTargetBlock("arg1")
        if(callback_enum && callback_enum.getFieldValue("ENUM_VAL")){
          var callback_type = callback_enum.getFieldValue("ENUM_VAL")
          if(callback_type && CallbackArguments[callback_type]){
            if(CallbackArguments[callback_type].length > i){
              target_argument = CallbackArguments[callback_type][i]
            }
          }
        }
        this.stick_block = blk
      }else{
        //change to global argument infos
        if(i < Code.arg_info.length){
          target_argument = Code.arg_info[i]
        }
      }

      if(target_argument){
        this.inputList[0].fieldRow[0].setValue(translate_str(target_argument.name))
        this.setOutput(true,target_argument.type)
        this.setWarningText()
      }else{
        this.inputList[0].fieldRow[0].setValue(translate_str('%{ARG_INVALID}'))
        this.setOutput('')
        this.setWarningText('Invalid argument')
      }
    }
  }
}

function handleAddCallbackSelect(blk){
  arg_config.last_select_id = blk.id
  //Assert blk is AddCallback
  //find arguments
  var callback_enum = blk.getInputTargetBlock("arg1")
  if(callback_enum && callback_enum.getFieldValue("ENUM_VAL")){
    var callback_type = callback_enum.getFieldValue("ENUM_VAL")
    if(arg_config.last_type != callback_type){
      arg_config.last_type = callback_type
      if(CallbackArguments[callback_type]){
        //Set arguments name
        Code.arg_info.length = 0
        for(let i=0;i<CallbackArguments[callback_type].length;i++){
          Code.arg_info.push(CallbackArguments[callback_type][i])
        }
      }else{
        Code.arg_info.length = 0
      }
    }
    //AddCallback last argument
    if(AddCallbackArguments[callback_type]){
      blk.getInput('arg3').fieldRow[0].setValue(translate_str(AddCallbackArguments[callback_type].name))
      blk.getInput('arg3').setCheck([AddCallbackArguments[callback_type].type])
    }else{
      blk.getInput('arg3').fieldRow[0].setValue("Not used")
    }
  }
}
function handleAddCallbackDelete(blkid){
  /*
  if(arg_config.last_select_id == blkid){
    Code.arg_info.length = 0
    arg_config.last_type = ""
  }*/
}

function handleArgumentChangeSelect(evt){
  if((
      /*evt.type == Blockly.Events.MOVE ||*/ 
      (evt.type == Blockly.Events.UI && evt.element == "click") //||
      /*(evt.type == Blockly.Events.CHANGE && Code.workspace.blockDB_[evt.blockId].type == "ModCallbacks")*/
    ) && evt.blockId){
      let blk = evt.getEventWorkspace_().getBlockById(evt.blockId)
      while(blk) {
          if (blk.type == "Isaac::AddCallback") {
              handleAddCallbackSelect(blk)
              break
          }
          blk = blk.getSurroundParent()
      }
  }else{
    //console.log(evt)
  }
  if(evt.type == Blockly.Events.DELETE){
    handleAddCallbackDelete(evt.blockId)
  }
}

function replaceFunc(block,func){
  let v = block.init
  block.init = function(){
    v.call(this)
    func.call(this)
  }
}


//called after workspace init
function inject_init(){
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
    "output": "table",
    "colour": 230,
    "tooltip": "%{FN_REF_TOOLTIP}",
    "helpUrl": ""
  }]))
  define_argument_blocks()


  init_game_blocks()
  //Arguments
  var arg_array_str = "<xml>"
  for(let i=0;i<10;i++) arg_array_str+="<block type='FUNC_ARG_"+i+"'></block>"
  arg_array_str += "</xml>"
  arg_array_str = Blockly.Xml.textToDom(arg_array_str).childNodes
  Code.arg_array = []
  for(let i=0;i<10;i++) Code.arg_array.push(arg_array_str[i])

  Code.arg_info = []
  // for(let i=0;i<10;i++){
  //   Code.arg_info.push({name:"argument("+i+")",type:null})
  // }

  //Code.arg_array has 10 elements
  Code.arg_arrays = []
  for(let i=0;i<10 + 1;i++){
    Code.arg_arrays[i] = []
    for(let j=0;j<i;j++){
      if(j == 0){//ignore the first argument 'this'
        continue
      }
      Code.arg_arrays[i].push(Code.arg_array[j])
    }
  }

  Code.workspace.registerToolboxCategoryCallback('Arguments',()=>{
    return Code.arg_arrays[Code.arg_info.length]
  })
  //Change callback argument names
  Code.workspace.addChangeListener(handleArgumentChangeSelect)
  
  // replaceFunc(Blockly.Blocks["Isaac::AddCallback"],function(){
  //
  // })
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
  return "https://moddingofisaac.com/docs" + url
}