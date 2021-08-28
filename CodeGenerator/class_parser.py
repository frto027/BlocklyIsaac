# MIT License

# Copyright (c) 2020-2021 frto027

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# from bs4 import BeautifulSoup
# from bs4 import element
from glob import glob
import re
LUA_DOC_DIR = "CodeGenerator/IsaacDocs"  # """CodeGenerator/LuaDocs"""
MOD_DOC_WEB_DIR = "" # "https://moddingofisaac.com/docs" see function get_blk_help at blockly_inject.js

# group 1 0 static
# group 2 1 const
# group 4 3 return type/value type
# group 5 4 func name / value name
# group 7 6 arg list (func only)
FUNC_NAME_REG = re.compile(r'^(static )?(const )?(([_a-zA-Z0-9:]+) )([a-zA-Z0-9_]+)( \((.*)\))?$')

def IsStatic(groups):
    return not groups[0] == None
def IsConst(groups):
    return not groups[1] == None
def IsFunc(groups):
    return groups[6] != None
def IsVar(groups):
    return groups[6] == None
def GetRetType(groups):
    assert groups[3] != None and IsFunc(groups)
    return groups[3]
def GetVarName(groups):
    assert groups[4] != None and IsVar(groups)
    return groups[4]
def GetFuncName(groups):
    assert groups[4] != None and IsFunc(groups)
    return groups[4]
def GetVarType(groups):
    assert groups[3] != None and IsVar(groups)
    return groups[3]
def GetArgListText(groups):
    assert IsFunc(groups)
    return groups[6]

# colours
name_to_color_map = {}
name_to_color_current = 0
def NameToColour(name):
    global name_to_color_current
    if not name in name_to_color_map:
        name_to_color_map[name] = str(name_to_color_current)
        name_to_color_current = name_to_color_current + 2
    return name_to_color_map[name]

# translate_map

translate_default = {}

translate_no_dup_texts = [
	"",
	"MC_INPUT_ACTION_CALLBACKARG",
    "MC_GET_CARD_CALLBACKARG",
    "MC_PRE_USE_ITEM_CALLBACKARG",
    "COLLIDE_WITH_ALL_GRID_ENTITIES",
    "THIS_FUNCTION_GETS_CALLED_WHEN",
]

def apply_translate(text,position_hash='',istype = False):
    # position_hash need to be a valid key!
    position_hash = position_hash.upper().replace('"','').replace(' ','_')
    position_hash = re.sub('[^A-Z0-9_]','',position_hash)

    key = text.upper().replace('"','').replace(' ','_')
    key = re.sub('[^A-Z0-9_]','',key)
    if istype:
        # type can be duplicated
        key = '__TYPE_' + key
    else:
        if key in translate_no_dup_texts:
            # text can not be duplicated
            dup_id = 0
            while '__TXT_'+str(dup_id) + '_'+key + position_hash in translate_default:
                dup_id = dup_id + 1
            key = '__TXT_'+str(dup_id) + '_'+key + position_hash
            translate_default[key] = text + '(dup ' + str(dup_id) + ')' + position_hash
        else:
            # text can be duplicated
            key = '__TXT_'+key
    if not key in translate_default:
        translate_default[key] = text
    return '%{' + key + '}'

# inherts
inhert = {
    "EntityBomb":"Entity",
    "EntityEffect":"Entity",
    "EntityFamiliar":"Entity",
    "EntityKnife":"Entity",
    "EntityLaser":"Entity",
    "EntityNPC":"Entity",
    "EntityPickup":"Entity",
    "EntityPlayer":"Entity",
    "EntityProjectile":"Entity",
    "EntityTear":"Entity",
    "GridEntityDoor":"GridEntity",
    "GridEntityPit":"GridEntity",
    "GridEntityPoop":"GridEntity",
    "GridEntityPressurePlate":"GridEntity",
    "GridEntityRock":"GridEntity",
    "GridEntitySpikes":"GridEntity",
    "GridEntityTNT":"GridEntity",
    # SampleList is a const VectorList(maybe)
    "SampleList":"VectorList"
}

typealias = {
    # 这些类型的使用和定义不一致，真不知道该怎么吐槽了
    "CardList":"CardConfigList",
    "CostumeList":"CostumeConfigList",
    "ItemList":"ItemConfigList",
    "PillList":"PillConfigList",
    "GridEntity":"GridEntityType",
    # ProjectilesMode is int
    "ProjectilesMode":"int",
    "LinecheckMode":"int",
    "Curses":"LevelCurse",

    "Number":"int", # If I need a float, you can give me a Number(by Blockly)
    "int":"float",
    "Boolean":"boolean",
    "String":"string",
}

# argument_type_dict = 
# {
#     "Level:GetName":{
#         "thisarg":"Level",
#         "arg1":"xxx",
#     }
# }
argument_type_dict = {}


callback_func_arg_reg = re.compile('Function Args:.?\\(([a-zA-Z\\[\\] ,]+)\\)')
callback_func_add_arg_reg = re.compile('Optional callback Args: ?([a-zA-Z]+)')

toolbox = {}
functions = {}
def parse_function_params(param_text):
    param_text = param_text.strip()
    ret = []
    if len(param_text) == 0:
        return ret
    for param in param_text.split(','):
        param = re.sub(r'\[([a-zA-Z0-9:]+)\]\([a-zA-Z0-9/\._]+\)',r'\1',param).strip()
        match = re.match(r'^([^ ]+)( +([^ ]+))?( *= *([^ ]+))?$',param)
        assert match, f'not match {param}'

        a_type = match.group(1)

        if a_type == 'bool':
            a_type = 'boolean'

        ret.append({
            'type':a_type,
            'name':match.group(3) if match.group(3) != None else '',
            'default':match.group(5)
        })
    return ret

    

def parse_class(text, class_file_name):
    lines = text.split('\n')
    if class_file_name in [
        'GlobalFunctions',
        'ModReference', # TODO we should parse ModReference
    ]:
        class_name = class_file_name
    else:
        class_name_match = re.match(r'# Class "([a-zA-Z0-9:_]+)"',lines[0]) 
        assert class_name_match, f'not found class name in {class_file_name}'
        class_name = class_name_match.group(1)

    # Functions Variables Operators
    current_subtitle = "None"
    tags = None

    for line in lines:
        if line.startswith('## '):
            current_subtitle = line[3:]
            continue
        if line.startswith('### '):
            if 'Children Classes' in line or 'Inherits from Class' in line:
                # we dont care about inhert relationship in documents
                continue
            # this is a Title of function, variable or operator
            assert f"aria-label='{current_subtitle}'" in line, f'unknown line format:{line}, file:{class_file_name}'
            tags = None
            continue
        if line.startswith('[ ](#)'):
            assert tags == None, 'already saw tags!'
            tags = line
            continue
        if line.startswith('#### '):
            assert f"aria-label='{current_subtitle}'" in line, f'unknown line format:{line}'

            line = line\
                .replace('[ItemConfig Card]','[ItemConfig::Card]')\
                .replace('[ItemConfig Item]','[ItemConfig::Item]')\
                .replace('[ItemConfig PillEffect]','[ItemConfig::PillEffect]')\
                .replace('[RoomDescriptor List]','[RoomDescriptor::List]')\
                .replace('[RoomConfig Spawn]','[RoomConfig::Spawn]')\
                .replace('[RoomConfig Entry]','[RoomConfig::Entry]')\
                .replace('[RoomConfig Room]','[RoomConfig::Room]')\
                .replace('[Mod Reference]','[ModReference]')

            line = re.sub(r'\[([a-zA-Z0-9:]+)\]\([a-zA-Z0-9/\._]+\)',r'\1',line[5:])
            line = re.sub(r'{[^}]+}$','',line.strip()).strip()
            assert not ('[' in line or ']' in line) , f'line should not contains markdown text:{line}'

            gp = FUNC_NAME_REG.match(line).groups()
            text = {}

            # we should parse the function header here
            if current_subtitle == 'Operators':
                operator_name = GetFuncName(gp)
                assert operator_name in ['__add','__sub','__div','__mul','__unm','__len']
                dup_hash = f'{class_name}::{operator_name}'
                text['type'] = f'"{class_name}::{operator_name}"'

                text['message0']=f'"[{apply_translate(GetRetType(gp),dup_hash,True)}]{apply_translate(operator_name,dup_hash)}%1'
                text['args0']='[{"type":"input_dummy"}'
                args = parse_function_params(GetArgListText(gp))
                assert len(args) == (1 if operator_name != '__len' else 0)
                if operator_name in ['__add','__sub','__div','__mul']:
                    text['message0'] += f' {apply_translate("this_target",dup_hash)}[{apply_translate(class_name,dup_hash,True)}]%2'
                    text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+ class_name +'","align":"RIGHT"}'
                    text['message0'] += f' {apply_translate(args[0]["name"],dup_hash)}[{apply_translate(args[0]["type"],dup_hash,True)}]%3'
                    text['args0'] += ',{"type":"input_value","name":"arg0","check":"'+ args[0]["type"] +'","align":"RIGHT"}'
                else:
                    text['message0'] += f' {apply_translate("this_target",dup_hash)}[{apply_translate(class_name,dup_hash,True)}]%2'
                    text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+ class_name +'","align":"RIGHT"}'
                text['message0'] += '"'
                text['args0'] += ']'
                text['inputsInline']="false"
                text['output']=f'"{GetRetType(gp)}"'
                text['colour']=NameToColour(GetRetType(gp))
                text['tooltip']=f'"{GetFuncName(gp)}"'
                href_url = f'/{class_file_name}.html#{GetFuncName(gp).lower()}'
                text['helpUrl']=f'()=>get_blk_help("{href_url}")'
                if not class_name in toolbox:
                    toolbox[class_name] = []
                toolbox[class_name].append(text)
                # generate function
                func_str = "function(block){return "
                ret_str = ""
                ORDER = 'ORDER_NONE' # len(xx)
                if operator_name in ['__div', '__mul']:
                    ORDER = 'ORDER_MULTIPLICATIVE'
                elif operator_name in ['__add','__sub']:
                    ORDER = 'ORDER_ADDITIVE'
                elif operator_name in ['__unm']:
                    ORDER = 'ORDER_UNARY'
                else:
                    assert operator_name == '__len'
                OPERATORS_MARK = {
                    '__add':'+',
                    '__sub':'-',
                    '__mul':'*',
                    '__div':'/',
                }
                if operator_name in operator_name in ['__add','__sub','__div','__mul']:
                    ret_str += f'Blockly.Lua.valueToCode(block, "thisobj", Blockly.Lua.{ORDER})+"{OPERATORS_MARK[operator_name]}"+Blockly.Lua.valueToCode(block, "arg0", Blockly.Lua.{ORDER})'
                elif operator_name == '__unm':
                    ret_str += f'"-"+Blockly.Lua.valueToCode(block, "thisobj", Blockly.Lua.{ORDER})'
                else:
                    assert operator_name == '__len'
                    ret_str += f'"len("+Blockly.Lua.valueToCode(block, "thisobj", Blockly.Lua.{ORDER})+")"'
                    ORDER = 'ORDER_HIGH' # we will generate a function call
                func_str += f'[{ret_str},Blockly.Lua.{ORDER}]'
                func_str += '}'
                functions[f'{class_name}::{GetFuncName(gp)}']=func_str

                self_argument_types = {}
                self_argument_types['thisobj']=class_name
                if len(args) >= 1:
                    self_argument_types['arg0']=args[0]['type']
                    assert len(args) == 1
                argument_type_dict[text['type'].strip('"')] = self_argument_types
            elif current_subtitle == 'Variables':
                variable_name = GetVarName(gp)
                var_type = GetVarType(gp)
                dup_hash = f'{class_name}::{variable_name}'

                assert not IsStatic(gp), f'{variable_name} at {class_file_name} is static'

                if class_name == 'RoomConfig::Room' and variable_name == 'Spawns':
                    assert var_type == 'SpawnList'
                    var_type = 'CppContainer::ArrayProxy::RoomConfigSpawns'

                text['type'] = f'"{class_name}::m_{variable_name}"'

                text['message0']=f'"[{apply_translate(var_type,dup_hash,True)}]{apply_translate(variable_name,dup_hash)}'

                text['message0'] += '%1'
                text['args0']='[{"type":"input_dummy"}'
                
                text['message0'] += f' {apply_translate("this_target",dup_hash)}[{apply_translate(class_name,dup_hash,True)}] %2'
                text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+class_name+'",align:"RIGHT"}'

                text['message0'] += '"'
                text['args0'] += ']'

                text['inputsInline']='false'
                text['output']=f'"{var_type}"'
                text['colour']=NameToColour(var_type)
                text['tooltip']=f'"{GetVarName(gp)}"'
                href_url = f'/{class_file_name}.html#{GetVarName(gp).lower()}'
                text['helpUrl']=f'()=>get_blk_help("{href_url}")'
                if not class_name in toolbox:
                    toolbox[class_name] = []
                toolbox[class_name].append(text)
                
                self_argument_types = {}
                self_argument_types['thisobj']=class_name
                argument_type_dict[text['type'].strip('"')] = self_argument_types
                func_str = "function(block){return "
                ret_str = f'Blockly.Lua.valueToCode(block,"thisobj",Blockly.Lua.ORDER_TABLE_ACCESS)+".{GetVarName(gp)}"'
                func_str += f'[{ret_str},Blockly.Lua.ORDER_HIGH]'
                func_str += '}'
                functions[f'{class_name}::m_{variable_name}']=func_str

                if not IsConst(gp):
                    # add setter for variable
                    text = text.copy()
                    text['type'] = f'"{class_name}::m_set_{variable_name}"'
                    text.pop('output')
                    text['message0']=f'"{apply_translate("set ",dup_hash)}{apply_translate(variable_name,dup_hash)}'
                    text['message0'] += '%1'
                    text['args0']='[{"type":"input_dummy"}'
                    text['message0'] += f' {apply_translate("this_target",dup_hash)}[{apply_translate(class_name,dup_hash,True)}] %2'
                    text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+class_name+'",align:"RIGHT"}'

                    # new value
                    text['message0']+=f' {apply_translate("new value",dup_hash)}[{apply_translate(var_type,dup_hash,True)}] %3'
                    text['args0'] += ',{"type":"input_value","name":"arg0","check":"'+var_type+'",align:"RIGHT"}'
                    text['message0'] += '"'
                    text['args0'] += ']'
                    text["previousStatement"]="null"
                    text["nextStatement"]="null"
                    text['colour']='230'

                    toolbox[class_name].append(text)
                    argument_type_dict[text['type'].strip('"')] = {
                        'thisobj':class_name,
                        'arg0':var_type
                    }

                    func_str = 'function(block){return Blockly.Lua.valueToCode(block, "thisobj", Blockly.Lua.ORDER_TABLE_ACCESS)+"."+"' + GetVarName(gp) + '="+Blockly.Lua.valueToCode(block, "arg0", Blockly.Lua.ORDER_NONE)+"\\n"}'
                    functions[text['type'].strip('"')] = func_str
            elif current_subtitle == 'Functions' or current_subtitle == 'Constructors':                
                func_name = GetFuncName(gp)
                dup_hash = f'{class_name}::{func_name}'
                is_ctor = current_subtitle == 'Constructors'
                is_global = class_name == 'GlobalFunctions'
                is_static = IsStatic(gp) or class_name == 'Isaac' or class_name == 'Input'
                # I dont think RegisterMod is a constructor
                if is_global and func_name == 'RegisterMod':
                    is_ctor = False

                # assert not IsStatic(gp), f'{func_name} at {class_md} is static'
                if IsConst(gp):
                    # These 'const function' means the value they return are const, instean of a real 'const function'
                    # Currently, we don't support const variable.
                    # So we just ignore it.
                    print(f'Warring: {func_name} at {class_file_name} is const, ignore const function')
                
                # function overload
                overload_tag = ''
                overload_tag_i = 0
                while f'{class_name}::{func_name}{overload_tag}' in functions:
                    overload_tag_i += 1
                    overload_tag = f'_overload{overload_tag_i}'
                if overload_tag_i != 0:
                    print(f"Warring: overload function {class_name}::{func_name}{overload_tag}")

                text['type'] = f'"{class_name}::{func_name}{overload_tag}"'

                self_argument_types = {}

                text['message0'] = '"'

                ret_type = GetRetType(gp)
                # fix the return type
                # Isaac.GetItemConfig should returns ItemConfig
                if class_name == 'Isaac' and func_name == 'GetItemConfig':
                    assert ret_type == 'Config'
                    ret_type = 'ItemConfig'
                if class_name == 'ItemConfig':
                    REPLACE_DICT = {
                        'CardList':'CppContainer::Vector::CardConfigList',
                        'CostumeList':'CppContainer::Vector::CostumeConfigList',
                        'ItemList':'CppContainer::Vector::ItemConfigList',
                        'PillList':'CppContainer::Vector::PillConfigList',
                    }
                    if ret_type in REPLACE_DICT:
                        ret_type = REPLACE_DICT[ret_type]
                if class_name == 'Level' and func_name == 'GetRooms':
                    assert ret_type == 'RoomDescriptor::List'
                    ret_type = 'CppContainer::ArrayProxy::RoomDescriptor'
                if class_name == 'MusicManager':
                    # every ID is wrong
                    if func_name in ['GetCurrentMusicID','GetQueuedMusicID']:
                        assert ret_type == 'MusicManager'
                        ret_type = 'Music'
                if class_name == 'EntityPlayer':
                    if func_name == 'GetMultiShotPositionVelocity':
                        assert ret_type == 'PosVel'
                        ret_type = 'PlayerTypes::PosVel'


                if ret_type != 'void':
                    text['message0'] += f'[{apply_translate(ret_type,dup_hash,True)}]'
                    text['output']=f'"{ret_type}"'
                else:
                    text["previousStatement"]="null"
                    text["nextStatement"]="null"

                if is_ctor:
                    assert ret_type == GetFuncName(gp), f'constructor return type mismatch {func_name} at {class_file_name}'
                    text['message0']+=f'{apply_translate(func_name + "_CTOR",dup_hash)}'
                else:
                    text['message0']+=f'{apply_translate(func_name,dup_hash)}'

                text['message0'] += '%1'
                text['args0']='[{"type":"input_dummy"}'
                
                arg_counter = 2
                if not is_static and not is_global and not is_ctor:
                    # add this
                    text['message0'] += f' {apply_translate("this_target",dup_hash)}[{apply_translate(class_name,dup_hash,True)}] %2'
                    text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+class_name+'",align:"RIGHT"}'
                    self_argument_types['thisobj']=class_name
                    arg_counter = 3


                # add function arguments

                args = parse_function_params(GetArgListText(gp))

                # fix param types

                # AddCallback 'function' type to 'ModCallbacks' enum
                if GetFuncName(gp) == 'AddCallback':
                    if class_name == 'Isaac':
                        assert args[1]['type'] == 'function'
                        args[1]['type'] = 'ModCallbacks'
                        assert args[2]['type'] == 'table'
                        args[2]['type'] = 'function'
                # Isaac.GridSpawn's first argument is a enum instead of GridEntity
                if GetFuncName(gp) == 'GridSpawn' and class_name == 'Isaac':
                    assert args[0]['type'] == 'GridEntity'
                    args[0]['type'] = 'GridEntityType'
                if class_name == 'TemporaryEffects':
                    for i in range(len(args)):
                        if args[i]['type'] == 'ItemConfig::NullItemID':
                            args[i]['type'] = 'NullItemID'
                if class_name == 'MusicManager':
                    # every ID is wrong
                    if func_name in ['Crossfade', 'Fadein', 'Play', 'Queue']:
                        assert args[0]['name'] == 'ID'
                        assert args[0]['type'] == 'MusicManager'
                        args[0]['type'] = 'Music'
                if class_name == 'EntityPlayer':
                    if (func_name in ['UseActiveItem', 'UseCard']) and args[1]['name'] == 'UseFlags':
                        assert args[1]['type'] == 'UseFlags'
                        assert args[1]['name'] == 'UseFlags'
                        args[1]['type'] = 'UseFlag'
                    if func_name == 'UsePill':
                        assert args[2]['type'] == 'UseFlags'
                        assert args[2]['name'] == 'UseFlags'
                        args[2]['type'] = 'UseFlag'

                arg_id = 0

                if GetFuncName(gp) == 'AddCallback' and class_name == 'ModReference':
                    # hack, ModReference::Addcallback has no arg0
                    arg_id = 1

                for arg in args:
                    text['message0'] += f' {apply_translate(arg["name"],dup_hash)}[{apply_translate(arg["type"],dup_hash,True)}] %{arg_counter}'
                    text['args0'] += ',{"type":"input_value","name":"arg'+str(arg_id)+'","check":"' + arg["type"] + '",align:"RIGHT"}'
                    self_argument_types['arg'+str(arg_id)] = arg['type']
                    arg_counter += 1
                    arg_id += 1

                text['message0'] += '"'
                text['args0'] += ']'

                text['inputsInline']='false'
                
                text['colour']=NameToColour(ret_type)
                text['tooltip']=f'"{GetFuncName(gp)}"'
                href_url = f'/{class_file_name}.html#{GetFuncName(gp).lower()}'
                text['helpUrl']=f'()=>get_blk_help("{href_url}")'
                if not class_name in toolbox:
                    toolbox[class_name] = []
                toolbox[class_name].append(text)
                
                argument_type_dict[text['type'].strip('"')] = self_argument_types
                func_str = "function(block){return "

                ret_str = ''
                # a.b(c)
                if not is_global and not is_ctor:
                    # a.
                    if is_static:
                        assert not ':' in class_name
                        ret_str += f'"{class_name}"'
                        ret_str += '+"."'
                    else:
                        ret_str += 'Blockly.Lua.valueToCode(block,"thisobj",Blockly.Lua.ORDER_TABLE_ACCESS)'
                        ret_str += '+":"'
                else:
                    # global function and constructor has no this
                    ret_str += '""'
                # b
                ret_str += f'+"{GetFuncName(gp)}"'

                #(c)
                ret_str += '+"("'
                
                for i in range(arg_id):
                    if GetFuncName(gp) == 'AddCallback' and class_name == 'ModReference':
                        # hack:skip arg0
                        if i == 0:
                            continue
                        if i > 1:
                            ret_str += '+","'
                    elif i > 0:
                        ret_str += '+","'
                    ret_str += f'+Blockly.Lua.valueToCode(block, "arg{i}", Blockly.Lua.ORDER_NONE)'

                ret_str += '+")"'
                if ret_type == 'void':
                    func_str += f'{ret_str}+"\\n"'
                else:
                    func_str += f'[{ret_str},Blockly.Lua.ORDER_HIGH]'
                func_str += '}'
                functions[text['type'].strip('"')]=func_str
            else:
                assert False, f'unknown subtitle {current_subtitle} in {class_file_name}'
        
# enumerate

def parse_enums(md_text,enum_name):

    assert enum_name != 'ModCallbacks', 'ModCallbacks file format is not same with others'

    found_header = None
    first_elem = True

    item_count = 0

    dup_hash = enum_name

    # print("GOT:" + enum_name)
    text = {}
    text["type"] = f'"{enum_name}"'
    text['message0'] = f'"[{apply_translate(enum_name,dup_hash,True)}] %1 "'
    text['args0'] = '[{"type": "field_dropdown","name": "ENUM_VAL","options":['
    help_url = f'/enums/{enum_name}.html'
    for line in md_text.split('\n'):
        # for enum, we only care about table lines
        if line in [
            "|DLC|Value|Enumerator|Comment|",
            "|DLC|Value|Enumerator|Icon|Comment|",
            "|DLC|Value|Enumerator|Value|Comment|",
            "|DLC|Value|Enumerator| Name in itempool.xml |Comment|",
            "|DLC|Value| Enumerator|internal id|possible stages|Comment|",
            "|DLC|Value|Enumerator|Ingame Color|Comment|",
            "|DLC|Value|Enumerator|Preview|Possible Gridindicies|Comment|"
            ]:
            found_header = line
            continue
        if not found_header:
            continue
        
        if not line.startswith('|[ ](#)'):
            continue

        if found_header == '|DLC|Value|Enumerator|Comment|':
            arr = line.split('|')
            DLC = arr[1]
            Value = arr[2]
            Enumerator = arr[3]
            Comment = arr[4] if len(arr) > 4 else ''
        elif found_header in [
            '|DLC|Value|Enumerator|Value|Comment|',
            '|DLC|Value|Enumerator|Icon|Comment|',
            '|DLC|Value|Enumerator|Ingame Color|Comment|',
            '|DLC|Value|Enumerator| Name in itempool.xml |Comment|',
        ]:
            # [_,DLC,Value,Enumerator,_,Comment,_] = line.split('|')
            arr = line.split('|')
            DLC = arr[1]
            Value = arr[2]
            Enumerator = arr[3]
            Comment = arr[5] if len(arr) > 6 else ''
        elif found_header in [
            '|DLC|Value| Enumerator|internal id|possible stages|Comment|',
            '|DLC|Value|Enumerator|Preview|Possible Gridindicies|Comment|'
            ]:
            #[_,DLC,Value,Enumerator,_,_,Comment,_] = line.split('|')
            arr = line.split('|')
            DLC = arr[1]
            Value = arr[2]
            Enumerator = arr[3]
            Comment = arr[6] if len(arr) > 6 else ''

        else:
            assert False, f'invalid header:{found_header}'

        # Collectibles ' Does not exist anymore '
        if enum_name == 'CollectibleType' and Enumerator == ' Does not exist anymore ':
            continue

        enum_item_names = re.match(r'([_A-Zx0-9]+) \{: .copyable \}',Enumerator)
        assert enum_item_names, f'invalid enum name:{Enumerator}'

        Comment = Comment.replace('<br>',' ').strip()

        field_name = enum_item_names.group(1)
        field_doc = Comment

        if not first_elem:
            text['args0'] += ','
        else:
            first_elem = False
        if len(field_doc) > 0:
            if len(field_doc) > 30:
                field_doc = field_doc[0:30] + '...'
            field_doc = apply_translate(field_doc,dup_hash)
            field_doc = '(' + field_doc.replace('"','\\"').replace('\n','') + ')'
        else:
            field_doc = ''

        text['args0'] += f'["{apply_translate(field_name,dup_hash)}{field_doc}","{field_name}"]'
        item_count += 1

        # print("name{"+field_name+"}")
        # print("doc{"+field_doc+"}")

    assert item_count > 0, f'empty enum {enum_name}'

    text['args0'] += ']}'
    text['args0'] += ']'
    text['output'] = f'"{enum_name}"'
    # text['output'] = '"Number"'
    text['tooltip']=f'"{enum_name}"'
    text['colour']='122'
    text['helpUrl']=f'()=>get_blk_help("{help_url}")'
    if not 'Enums' in toolbox:
        toolbox['Enums'] = []
    toolbox['Enums'].append(text)

    # functions for enum
    func_str = "function (block){ return ['" + enum_name + ".'+ block.getFieldValue('ENUM_VAL'),Blockly.Lua.ORDER_HIGH]}"
    functions[text['type'].strip('"')] = func_str

    # all enums are number
    typealias[enum_name]='Number'

    # record all enum types
    enum_types.append(enum_name)



callback_args = {}
callback_add_args = {}
def parse_callback_args(args_text, callback_name):
    ret = []
    args_text = args_text.strip()
    if len(args_text) == 0:
        return ret
    for arg in args_text.split(',<br>'):
        assert arg.count(',') == 0, f'invalid argument text:{arg}'
        no_padding_arg = arg.strip()

        
        # type A: Name [[Type](type.md)]
        match = re.match(r'(([A-Za-z0-9_]+) )?\[\[([a-zA-Z0-9_]+)\](\(.*\))?\]',no_padding_arg)
        if match:
            Type = match.group(3)
            Name = match.group(2)
        else:
            # type B: Name [Type](type.md)
            match = re.match(r'(([A-Za-z0-9_]+) )?\[([a-zA-Z0-9_]+)\](\(.*\))?',no_padding_arg)
            if match:
                Type = match.group(3)
                Name = match.group(2)
            else:
                # type
                match = re.match(r'([a-zA-Z0-9]+)\*?',no_padding_arg)
                if match:
                    Type = match.group(1)
                    Name = None
                else:
                    assert False, f'cant match argument "{no_padding_arg}", all is {args_text}'
        assert Type != None, f'cant match type for argument "{no_padding_arg}"'

        ret.append({
            "type":Type,
            "name":f'[{apply_translate(Type,callback_name,True)}]' +
                (apply_translate(Name,callback_name) if Name != None else '')
        })
    return ret
enum_types = []
def parse_mod_callback_enum(md_text):
    assert md_text.startswith('# Enum "ModCallbacks"'), 'invalid mod_callback_enum file'

    enum_name = 'ModCallbacks'
    first_elem = True
    dup_hash = "ModCallbacks"

    text = {}
    text["type"] = f'"{enum_name}"'
    text['message0'] = f'"[{apply_translate(enum_name,dup_hash,True)}] %1 "'
    text['args0'] = '[{"type": "field_dropdown","name": "ENUM_VAL","options":['
    help_url = f'/enums/ModCallbacks.html'

    item_count = 0

    for enum_item in md_text.split('### ')[1:]:
        assert enum_item.count('|DLC|Value|Name|Function Args| Optional Args|') == 1 and enum_item.count('|:--|:--|:--|:--|:--|') == 1
        items_line = enum_item.split('|:--|:--|:--|:--|:--|')[1].split('\n')[1]
        desc_text = enum_item.split('\n')[1]

        assert items_line.count('|') == 6, f'modcallbacks bad format:{items_line}'
        [_,DLC,Value,Name,FunctionArgs,OptionalArgs,_] = items_line.split('|')
        Name = re.match(r'([_A-Z0-9]+) +\{: .copyable \}',Name)
        assert Name, f'invalid enum name:{Name}, all is {items_line}'
        Name = Name.group(1)

        FunctionArgs = FunctionArgs.strip()
        if FunctionArgs != '-':
            assert FunctionArgs.startswith('(') and FunctionArgs.endswith(')'), f'Bad function args {FunctionArgs}'
            FunctionArgs = FunctionArgs[1:][:-1]
        else:
            FunctionArgs = ''
        if OptionalArgs.strip() == '-':
            OptionalArgs = ''

        m_callback_args = parse_callback_args(FunctionArgs, Name)
        m_callback_add_args = parse_callback_args(OptionalArgs, Name)

        callback_args[Name] = m_callback_args
        assert len(m_callback_add_args) <= 1
        if len(m_callback_add_args) == 1:
            callback_add_args[Name] = m_callback_add_args[0]

        field_name = Name
        field_doc = desc_text

        if not first_elem:
            text['args0'] += ','
        else:
            first_elem = False
        if len(field_doc) > 0:
            if len(field_doc) > 30:
                field_doc = field_doc[0:30] + '...'
            field_doc = apply_translate(field_doc,dup_hash)
            field_doc = '(' + field_doc.replace('"','\\"').replace('\n','') + ')'
        else:
            field_doc = ''

        text['args0'] += f'["{apply_translate(field_name,dup_hash)}{field_doc}","{field_name}"]'
        item_count += 1
    
    assert item_count > 0

    text['args0'] += ']}'
    text['args0'] += ']'
    text['output'] = f'"{enum_name}"'
    # text['output'] = '"Number"'
    text['tooltip']=f'"{enum_name}"'
    text['colour']='122'
    text['helpUrl']=f'()=>get_blk_help("{help_url}")'
    if not 'Enums' in toolbox:
        toolbox['Enums'] = []
    toolbox['Enums'].append(text)

    # functions for enum
    func_str = "function (block){ return ['" + enum_name + ".'+ block.getFieldValue('ENUM_VAL'),Blockly.Lua.ORDER_HIGH]}"
    functions[text['type'].strip('"')] = func_str

    # all enums are number
    typealias[enum_name]='Number'

    # record all enum types
    enum_types.append(enum_name)


for enum_md in glob(f'{LUA_DOC_DIR}/docs/enums/*.md'):
    enum_name = enum_md.split('\\')[-1][:-3]
    with open(enum_md) as f:
        if enum_name == 'ModCallbacks':
            parse_mod_callback_enum(f.read()) 
        else:
            parse_enums(f.read(),enum_name)

            
for class_md in glob(f'{LUA_DOC_DIR}/docs/*.md'):
    class_name = class_md.split('\\')[-1][:-3]
    if class_name in [
        'PLACEHOLDER',
        'index',
        ]:
        continue
    # print(f'parse class file : {class_md}')

    with open(class_md) as f:
        parse_class(f.read(),class_name)


#patch: replace all integer to math_number
type_output_replace = {
    "int":"Number",
    "float":"Number",
    "boolean":"Boolean",
    "string":"String"
}
for clss in toolbox:
    for text in toolbox[clss]:
        if 'output' in text and text['output'].strip('"') in type_output_replace:
            text['output'] = '"' + type_output_replace[text['output'].strip('"')] + '"'



#patch: Generate toolbox with some text
def toolboxBlockText(block):
    if block == 'Isaac::AddCallback':
        return '<value name="arg1"><block type="ModCallbacks"></block></value>'+\
            '<value name="arg2"><block type="lambda_func"></block></value>'+\
            '<value name="arg3"><shadow type="logic_null"></shadow></value>'
    if block == 'ModReference::AddCallback':
        return '<value name="arg1"><block type="ModCallbacks"></block></value>'+\
            '<value name="arg2"><block type="lambda_func"></block></value>'+\
            '<value name="arg3"><shadow type="logic_null"></shadow></value>'
    if block == 'GlobalFunctions::RegisterMod':
        return '<value name="arg0"><shadow type="text"><field name="TEXT">MyBlocklyMod</field></shadow></value>'+\
            '<value name="arg1"><shadow type="math_number"><field name="NUM">1</field></shadow></value>'
    if block == 'Isaac::GetPlayer':
        return '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'
    if block == 'Game::GetPlayer':
        return '<value name="thisobj"><shadow type="Game::Game"></shadow></value>'+\
        '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'
    if block == 'EntityNPC::FireProjectiles':
        # the FireProjectiles argument is not documented, we need a comment here
        return '<value name="arg2"><shadow type="math_number"><field name="NUM">0</field>'+\
        '<comment pinned="false" h="240.66668701171875" w="738">%{ENTITYNPC_FIREPROJECTILES_ARGUMENT_PROJECTILE_MODE}</comment>'+\
        '</shadow></value>'
    if block == 'Room::CheckLine':
        return '<value name="thisobj"><block type="Game::GetRoom"><value name="thisobj"><block type="Game::Game"></block></value></block></value>'+\
        '<value name="arg0"><shadow type="Vector::Vector" inline="true">'+\
        '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'+\
        '<value name="arg1"><shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow></value>'+\
        '<value name="arg1"><shadow type="Vector::Vector" inline="true"><value name="arg0">'+\
        '<shadow type="math_number"><field name="NUM">0</field></shadow></value><value name="arg1">'+\
        '<shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow></value>'+\
        '<value name="arg2"><shadow type="math_number"><field name="NUM">0</field>'+\
        '<comment pinned="false" h="192" w="605">%{ROOM_CHECKLINE_LINECHECKMODE_COMMENT}</comment></shadow></value>'+\
        '<value name="arg3"><shadow type="math_number"><field name="NUM">0</field></shadow></value><value name="arg4">'+\
        '<shadow type="logic_boolean"><field name="BOOL">FALSE</field></shadow></value><value name="arg5">'+\
        '<shadow type="logic_boolean"><field name="BOOL">FALSE</field></shadow></value>'
    # the default value
    ret = ''
    if block in argument_type_dict:
        type_dict = argument_type_dict[block]
        for argname in type_dict:
            if type_dict[argname] == 'Game':
                ret += '<value name="{arg}"><shadow type="Game::Game"></shadow></value>'.format(arg=argname)
            if type_dict[argname] == 'EntityPlayer':
                ret += ('<value name="{arg}"><block type="Isaac::GetPlayer">'+\
                    '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'+\
                    '</block></value>').format(arg=argname)
            if type_dict[argname] == 'MusicManager':
                ret += '<value name="{arg}"><shadow type="MusicManager::MusicManager"></shadow></value>'.format(arg=argname)
            if type_dict[argname] == 'Font':
                ret += ('<value name="{arg}"><shadow type="Game::GetFont">'+\
                    '<value name="thisobj"><shadow type="Game::Game"></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'Level':
                ret += ('<value name="{arg}"><shadow type="Game::GetLevel">'+\
                    '<value name="thisobj"><shadow type="Game::Game"></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'Room':
                ret += ('<value name="{arg}"><shadow type="Game::GetRoom">'+\
                    '<value name="thisobj"><shadow type="Game::Game"></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'Seeds':
                ret += ('<value name="{arg}"><shadow type="Game::GetSeeds">'+\
                    '<value name="thisobj"><shadow type="Game::Game"></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'SFXManager':
                ret += ('<value name="{arg}"><shadow type="SFXManager::SFXManager"></shadow></value>').format(arg=argname)
            if type_dict[argname] in enum_types:
                ret += ('<value name="{arg}"><shadow type="{enum_type}"></shadow></value>').format(arg=argname, enum_type=type_dict[argname])
            if type_dict[argname] == 'boolean':
                ret += ('<value name="{arg}"><shadow type="logic_boolean"><field name="BOOL">FALSE</field></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'int' or type_dict[argname] == 'float':
                ret += ('<value name="{arg}"><shadow type="math_number"><field name="NUM">0</field></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'Vector':
                ret += ('<value name="{arg}"><shadow type="Vector::Vector" inline="true">'+\
                    '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'+\
                    '<value name="arg1"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'TemporaryEffects':
                ret += ('<value name="{arg}"><shadow type="EntityPlayer::GetEffects">'+\
                '<value name="thisobj"><shadow type="Isaac::GetPlayer">'+\
                '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'+\
                '</shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'TemporaryEffect':
                ret += ('<value name="{arg}"><shadow type="TemporaryEffects::GetCollectibleEffect">'+\
                '<value name="thisobj"><shadow type="EntityPlayer::GetEffects"><value name="thisobj">'+\
                '<shadow type="Isaac::GetPlayer"><value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow>'+\
                '</value></shadow></value><value name="arg0"><shadow type="CollectibleType">'+\
                '<field name="ENUM_VAL">COLLECTIBLE_SAD_ONION</field></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'string':
                ret += ('<value name="{arg}"><shadow type="text"><field name="TEXT"></field></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'TearParams':
                ret += ('<value name="{arg}"><shadow type="EntityPlayer::GetTearHitParams">'+\
                '<value name="thisobj"><shadow type="Isaac::GetPlayer"><value name="arg0"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value></shadow></value><value name="arg0">'+\
                '<shadow type="WeaponType"><field name="ENUM_VAL">WEAPON_TEARS</field></shadow></value><value name="arg1">'+\
                '<shadow type="math_number"><field name="NUM">1</field></shadow></value><value name="arg2">'+\
                '<shadow type="math_number"><field name="NUM">1</field></shadow></value><value name="arg3">'+\
                '<shadow type="logic_null"></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'RoomDescriptor':
                ret += ('<value name="{arg}"><shadow type="Level::GetCurrentRoomDesc"><value name="thisobj">'+\
                '<shadow type="Game::GetLevel"><value name="thisobj"><shadow type="Game::Game"></shadow></value></shadow>'+\
                '</value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'RoomConfig::Room':
                ret += ('<value name="{arg}"><block type="RoomDescriptor::m_Data">'+\
                '<value name="thisobj"><shadow type="Level::GetCurrentRoomDesc">'+\
                '<value name="thisobj"><shadow type="Game::GetLevel"><value name="thisobj"><shadow type="Game::Game">'+\
                '</shadow></value></shadow></value></shadow></value></block></value>').format(arg=argname)
            if type_dict[argname] == 'RoomConfig::Spawn':
                ret += ('<value name="{arg}"><block type="CppContainer::ArrayProxy::RoomConfigSpawns::Get">'+\
                '<value name="thisobj"><block type="RoomConfig::Room::m_Spawns"><value name="thisobj">'+\
                '<block type="RoomDescriptor::m_Data"><value name="thisobj"><shadow type="Level::GetCurrentRoomDesc">'+\
                '<value name="thisobj"><shadow type="Game::GetLevel"><value name="thisobj"><shadow type="Game::Game">'+\
                '</shadow></value></shadow></value></shadow></value></block></value></block></value><value name="arg0">'+\
                '<shadow type="math_number"><field name="NUM">0</field></shadow></value></block></value>').format(arg=argname)
            if type_dict[argname] == 'RoomConfig::Entry':
                ret += ('<value name="{arg}"><block type="RoomConfig::Spawn::PickEntry"><value name="thisobj">'+\
                '<block type="CppContainer::ArrayProxy::RoomConfigSpawns::Get"><value name="thisobj">'+\
                '<block type="RoomConfig::Room::m_Spawns"><value name="thisobj"><block type="RoomDescriptor::m_Data">'+\
                '<value name="thisobj"><shadow type="Level::GetCurrentRoomDesc"><value name="thisobj">'+\
                '<shadow type="Game::GetLevel"><value name="thisobj"><shadow type="Game::Game"></shadow>'+\
                '</value></shadow></value></shadow></value></block></value></block></value><value name="arg0">'+\
                '<shadow type="math_number"><field name="NUM">0</field></shadow></value></block></value><value name="arg0">'+\
                '<shadow type="math_number"><field name="NUM">0</field></shadow></value></block></value>').format(arg=argname)
            if type_dict[argname] == 'ItemConfig::Item':
                ret += ('<value name="{arg}"><shadow type="ItemConfig::GetCollectible"><value name="thisobj">'+\
                '<shadow type="ItemConfig"><field name="ENUM_VAL">CHARGE_NORMAL</field></shadow></value>'+\
                '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'PathFinder':
                ret += ('<value name="{arg}"><block type="EntityNPC::m_Pathfinder"></block></value>').format(arg=argname)
            if type_dict[argname] == 'KColor':
                ret += ('<value name="{arg}"><shadow type="KColor::KColor"><value name="arg0"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value><value name="arg1"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value><value name="arg2"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value><value name="arg3"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'PlayerTypes::PosVel':
                ret += ('<value name="{arg}"><shadow type="EntityPlayer::GetMultiShotPositionVelocity">'+\
                '<value name="thisobj"><shadow type="Isaac::GetPlayer"><value name="arg0"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value></shadow></value><value name="arg0"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value><value name="arg1"><shadow type="WeaponType">'+\
                '<field name="ENUM_VAL">WEAPON_TEARS</field></shadow></value><value name="arg2">'+\
                '<shadow type="Vector::Vector" inline="true"><value name="arg0"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value><value name="arg1"><shadow type="math_number">'+\
                '<field name="NUM">0</field></shadow></value></shadow></value><value name="arg3">'+\
                '<shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'ItemPool':
                ret += ('<value name="{arg}"><shadow type="Game::GetItemPool"><value name="thisobj"><shadow type="Game::Game"></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'ItemConfig::Card':
                ret += ('<value name="{arg}"><shadow type="ItemConfig::GetCard"><value name="thisobj"><shadow type="ItemConfig"><field name="ENUM_VAL">CHARGE_NORMAL</field></shadow></value><value name="arg0"><shadow type="Card"><field name="ENUM_VAL">CARD_RANDOM</field></shadow></value></shadow></value>').format(arg=argname)
            if type_dict[argname] == 'HUD':
                ret += ('<value name="{arg}"><shadow type="Game::GetHUD"><value name="thisobj"><shadow type="Game::Game"></shadow></value></shadow></value>').format(arg=argname)

    return ret


# generate json

json_str = None

# toolbox["GlobalFunctions"] is global function
# toolbox["ItemConfig::Item"]
# toolbox["Game"]
# ...
for clss in toolbox:
    for text in toolbox[clss]:
        txt = None
        for k in text:
            if txt == None:
                txt = '{'
            else:
                txt += ','
            txt += '"' + k + '":' + text[k]
        txt += "}"
        if json_str == None:
            json_str = '['
        else:
            json_str += ','
        json_str += txt

if json_str == None:
    json_str = '['

json_str += ']'

# generate function
func_str = ""
for bname in functions:
    func_str += "Blockly.Lua['"+ bname +"'] = " + functions[bname]
    func_str += '\n'

# generate toolbox xml
toolbox_xml = ""
for clss in toolbox:
    name = clss.strip('::')
    if clss == "":
        name = "Global"
    name = apply_translate(name,'toolbox',True)
    toolbox_xml += '<category name="'+ name +'" colour="'+NameToColour(name)+'">'
    for text in toolbox[clss]:
        toolbox_xml += '<block type="'+ text['type'].strip('"') +'">' + toolboxBlockText(text['type'].strip('"')) + '</block>'
    toolbox_xml += '</category>'

# generate CallbackArguments and AddCallbackArguments
cbargs = "var CallbackArguments = {"
for k in callback_args:
    cbargs += '"' + k + '":[{name:"_",type:undefined}'
    for arg in callback_args[k]:
        cbargs += ',{name:"' + arg["name"] + '",type:"'+arg["type"] + '"}'
    cbargs += ']'
    cbargs += ','
cbargs += '}\n'
cbargs += "var AddCallbackArguments = {"
for k in callback_add_args:
    cbargs += '"' + k + '":{name:"' + callback_add_args[k]['name'] + '",type:"'+callback_add_args[k]['type'] + '"},'
cbargs += '}\n'


jsoutput = "function init_game_blocks(){\n"
jsoutput += "Blockly.defineBlocksWithJsonArray(translate_tjson("+json_str + '))\n'
jsoutput += "}\n"
jsoutput += func_str + '\n'
jsoutput += "var toolbox_elems_xml='" + toolbox_xml+"'\n"
jsoutput += cbargs

# inherts
for k in inhert:
    jsoutput += 'parent_of_block_type["'+k+'"]="'+inhert[k]+'"\n'

#aliase
for k in typealias:
    jsoutput += 'type_aliase["' + k + '"]="' + typealias[k]+'"\n'

with open('./game_blocks.js','w') as f:
    f.write(jsoutput)

# generate translate table

translate_files = [
    'code_translate/en.js',
    'code_translate/zh-hans.js']

def translate_already_def(linesarr,translate):
    for k in linesarr:
        if k.startswith('"' + translate + '"'):
            return True
    return False

for trans_file in translate_files:
    try:
        with open(trans_file,encoding='utf-8') as f:
            texts = f.readlines()
    except FileNotFoundError:
        texts = []
    while len(texts) > 0 and not texts.pop().startswith('}'):
        pass
    if len(texts) == 0:
        texts.append('TMSG={\n')
    for k in translate_default:
        default_line_str = '"'+k+'":"' + translate_default[k].replace('\n','\\n').replace('"','\\"') + '",\n'
        # 让旧值浮上来，默认值沉下去
        if default_line_str in texts:
            texts.remove(default_line_str)
        if not translate_already_def(texts,k):
            texts.append(default_line_str)
    texts.append('}\n')
    with open(trans_file,'w',encoding='utf-8') as f:
        f.writelines(texts)

