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

# """
# group:
# 1 0 static
# 2 1 const
# 3 2 返回值（整体）包含(4 7)
# 4 3 返回值类型
# 7 6 返回值的&标记

# 8 7 命名空间/类名
# 10 9 函数/成员名字
# """
# FUNC_NAME_REG = re.compile('^(static )?(const )?((([_a-zA-Z0-9]+::)*([_a-zA-Z0-9]+))(&)? )?(([_a-zA-Z0-9]+::)*)([_a-zA-Z0-9]+)$')

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
# def IsStatic(groups):
#     return not groups[0] == None
# def IsConst(groups):
#     return not groups[1] == None
# def GetRetType(groups):
#     if IsCtor(groups):
#         return GetClassName(groups).strip('::')
#     if groups[3] == None:
#         return None
#     return convert_text_type(groups[3])
# def IsRetRef(groups):
#     return not groups[6] == None
# def GetClassName(groups):
#     return groups[7]
# def GetName(groups):
#     return groups[9]
# def IsCtor(groups):
#     return GetClassName(groups).strip('::').split('::')[-1] == GetName(groups)

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
    # I don't know what ProjectilesMode is...
    "ProjectilesMode":"integer",
    "Curses":"LevelCurse",

    "Number":"integer", # If I need a float, you can give me a Number(by Blockly)
    "integer":"float",
    "Boolean":"boolean",
    "String":"string",
}

# inhert_cluster = {}

# 手动处理不合法的定义
def convert_text_name(text):
    # Wow,I got a very const member just like "const const Costume& ItemConfig::Item::Costume"?
    text = text.replace('const const','const')
    # LuaArrayProxy..........
    text = text.replace('LuaArrayProxy<RoomDescriptor, true>','table')
    # I don't care about unsigned in lua
    text = text.replace('unsigned int','int')
    text = text.replace('u8','int').replace('u16','int').replace('u32','int')
    text = text.replace('s8','int').replace('s16','int').replace('s32','int')
    # LevelStage (UserData) Game::GetLastDevilRoomStage the function in unusable, but I still translate it
    text = text.replace('LevelStage (UserData)','LevelStage')
    return text
def convert_text_type(text):
    if text in ['int','unsigned int','u16']:
        return 'integer'
    
    if text.startswith("Config::"):
        return "ItemConfig::"+text
    return text
# 获得兼容类型
# def getChildTypesWithSelf(typename):
#     if typename in inhert_cluster:
#         return inhert_cluster[typename]
#     return [typename]

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
def parse_class_text(text,is_namespace,file_path):
    soup = BeautifulSoup(text,'html.parser')
    for item in soup.find_all(attrs={"class":'memitem'}):
        item_table = item.find('table', attrs={"class":'memname'})
        item_name = item_table.find('td', attrs={"class":'memname'}).text.strip()
        item_name = convert_text_name(item_name)

        param_types = item_table.find_all(attrs={"class":'paramtype'})
        param_names = item_table.find_all(attrs={"class":'paramname'})

        self_argument_types = {}

        item_type = 'unknown'
        if len(param_names) == 0:
            item_type = 'member'
        else:
            if is_namespace:
                item_type = 'glofunc'
            else:
                item_type = 'memfunc'
            if len(param_names) == 1 and len(param_types) == 0:
                param_names = []
        
        assert item_type in ['member','glofunc','memfunc'], 'what type is it?' 
        assert len(param_names) == len(param_types), 'how many params?'

        param_types = [convert_text_type(x.text.strip()) for x in param_types]
        param_names = [x.text.strip().rstrip(',') for x in param_names]
        params = [[_type,_name] for _type, _name in zip(param_types, param_names)]

        if len(params) == 1 and params[0][0] == 'void' and params[0][1] == '':
            # this is some functions such as 'Font::font(void)', remove the parameter list
            params = []

        gp = FUNC_NAME_REG.match(item_name).groups()
        
        # href_url = file_path + item.find_previous_sibling(attrs={"class":'memtitle'}).find('a')['href']
        url_path = GetClassName(gp) \
                        .strip(':') \
                        .replace('::','_') \
                        .replace(':','/')
        if len(url_path) == 0:
            # Global Functions
            url_path = 'GlobalFunctions'
        url_anchor = GetName(gp).lower()
        href_url = f'/{url_path}.html#{url_anchor}'
        # print(href_url)

        # fix param list for function 'GetPtrHash' manually
        if GetName(gp)=='GetPtrHash':
            if len(param_types) == 0 and len(param_names) == 0 :
                param_types = ['Object']
                param_names = ['object']
                params = [[_type,_name] for _type, _name in zip(param_types, param_names)]
            else:
                print('Warring:please look at the block "GetPtrHash", it maybe not correct.')
                import traceback
                traceback.print_stack()
        # fix param type for 'Isaac.GridSpawn' manually
        if GetClassName(gp) == 'Isaac::' and GetName(gp) == 'GridSpawn':
            if len(param_types) > 0 and param_types[0] == 'GridEntity':
                param_types[0] = 'GridEntityType'
            else:
                print('Warring:please look at the block "Isaac.GridSpawn", it maybe not correct.')
                import traceback
                traceback.print_stack()

        # fix params for __unm
        if GetName(gp) == '__unm':
            param_types = []
            param_names = []
            params = []


        text = {}
        if item_type == 'member':
            type_prefix = 'm_'
        else:
            type_prefix = ''

        dup_hash = type_prefix + GetClassName(gp)+GetName(gp)

        text['type'] = '"'+ type_prefix + GetClassName(gp)+GetName(gp) + '"'
        text['message0'] = '"'
        if not GetRetType(gp) == None:
            text['message0'] += '[' + apply_translate(GetRetType(gp).strip('::'),dup_hash,True) + ']'
        else:
            text["previousStatement"]="null"
            text["nextStatement"]="null"
        if IsCtor(gp):
            text['message0'] += apply_translate(GetName(gp)+"_CTOR",dup_hash)
        else:
            text['message0'] += apply_translate(GetName(gp),dup_hash)
        text['args0']="["

        # message0
        text["message0"]+= "%1"
        text['args0']+='{"type":"input_dummy"}'

        arg_counter = 2

        if not is_namespace and not IsStatic(gp) and not IsCtor(gp):
            text['message0'] += " "+apply_translate("this_target",dup_hash)+"[" + apply_translate(GetClassName(gp).strip('::'),dup_hash,True) +"] %2"
            text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+GetClassName(gp).strip('::')+'",align:"RIGHT"}'
            self_argument_types["thisobj"] = GetClassName(gp).strip('::')
            arg_counter = 3

        # arguments
        for i in range(len(params)):
            text['message0'] += apply_translate(param_names[i],dup_hash) + "[" + apply_translate(param_types[i],dup_hash,True) + "]" + " %" + str(arg_counter)
            # arg = ',{"type":"input_value","name":"arg'+str(i)+'","check":['
            # types = getChildTypesWithSelf(param_types[i])
            # for j in range(len(types)):
            #     if j > 0:
            #         arg += ','
            #     arg += '"' + types[j] + '"'
            # arg+=']}'
            arg = ',{"type":"input_value","name":"arg'+str(i)+'","check":"' + param_types[i] + '",align:"RIGHT"}'
            self_argument_types['arg'+str(i)] = param_types[i]
            text['args0'] += arg
            arg_counter = arg_counter + 1
        text['message0'] += '"'
        text['args0']+="]"

        text['inputsInline']="false"
        if not GetRetType(gp) == None:
            text['output']='"'+GetRetType(gp)+'"'
        if GetRetType(gp) == None:
            text['colour'] = "230"
        else:
            text['colour'] = NameToColour(GetRetType(gp).strip('::'))
        text['tooltip']='"'+GetName(gp)+'"'
        text['helpUrl']='()=>get_blk_help("' + href_url + '")'

        if GetClassName(gp) == None:
            # global function
            print("glob func "+GetName(gp))
            pass
        elif not GetClassName(gp) in toolbox:
            toolbox[GetClassName(gp)]=[]
        toolbox[GetClassName(gp)].append(text)

        # function (return a.b(c))

        func_str = "function(block){return "
        ret_str = ""

        OPERATORS_MARK = {
            '__add':'+',
            '__sub':'-',
            '__mul':'*',
            '__div':'/',
            '__unm':'-'
        }

        if GetName(gp) in ['__add','__sub','__div','__mul','__unm']:
            assert not is_namespace and not IsStatic(gp) and not IsCtor(gp)
            ORDER = 'ORDER_MULTIPLICATIVE' if GetName(gp) in ['__div','__mul'] else 'ORDER_ADDITIVE' if GetName(gp) in ['__add','__sub'] else 'ORDER_UNARY'
            if GetName(gp) != '__unm':
                ret_str += "Blockly.Lua.valueToCode(block, 'thisobj', Blockly.Lua." + ORDER + ")"
                ret_str += "+"
            ret_str += "'" + OPERATORS_MARK[GetName(gp)] + "'"
            ret_str += "+"
            if GetName(gp) != '__unm':
                ret_str += "Blockly.Lua.valueToCode(block, 'arg0', Blockly.Lua." + ORDER + ")"
            else:
                ret_str += "Blockly.Lua.valueToCode(block, 'thisobj', Blockly.Lua." + ORDER + ")"
            assert GetRetType(gp) != None
            func_str += "[" + ret_str + ",Blockly.Lua." + ORDER + "]"
        else:
            # a. or a:
            if not is_namespace and not IsStatic(gp):
                if not IsCtor(gp):
                    ret_str += "Blockly.Lua.valueToCode(block, 'thisobj', Blockly.Lua.ORDER_TABLE_ACCESS)"
                    if item_type == 'member':
                        ret_str += "+'.'"
                    else:
                        ret_str += "+':'"
                else:
                    ret_str += '""'
            else:
                # It is okay for global functions
                ret_str += '"' + GetClassName(gp).replace('::','.') + '"'
            # b
            ret_str += "+'" + GetName(gp) + "'"
            # (c)
            if not item_type == 'member':
                ret_str += '+"("'

                for i in range(len(params)):
                    if i > 0:
                        ret_str += "+','"
                    ret_str += "+Blockly.Lua.valueToCode(block, 'arg" + str(i) +"', Blockly.Lua.ORDER_NONE)"

                ret_str += '+")"'

            if GetRetType(gp) == None:
                func_str += ret_str + '+"\\n"'
            else:
                if item_type == 'member':
                    func_str += "[" + ret_str + ",Blockly.Lua.ORDER_HIGH]"
                else:
                    func_str += "[" + ret_str + ",Blockly.Lua.ORDER_HIGH]"

        func_str+="}"
        functions[text['type'].strip('"')] = func_str
        
        argument_type_dict[text['type'].strip('"')] = self_argument_types
        # print(text)

        # create setter for a member
        if item_type == 'member' and not IsConst(gp) and not GetRetType(gp) == None:
            # lots of members have no type, so I can't generate setter for them.
            # assert not GetRetType(gp) == None, 'why class member has no type?\nfile:{filepath}\ntext:{text}'.format(filepath=file_path, text=str(text))
            text = text.copy()
            text['type']='"set' + text['type'].strip('"') + '"'
            text.pop('output')
            text['args0'] = text['args0'].rstrip(']') + ',{"type":"input_value","name":"arg0","check":"' + GetRetType(gp) + '",align:"RIGHT"}' + ']'
            # add 'set' prefix
            text['message0'] = text['message0'].replace(']'+apply_translate(GetName(gp),dup_hash),']' + apply_translate('set ',dup_hash) + apply_translate(GetName(gp),dup_hash), 1)
            # add 'new value' to message
            text['message0']=text['message0'].rstrip('"') + apply_translate('new value',dup_hash) + '[' + apply_translate(GetRetType(gp),dup_hash, True) + '] %' + str(arg_counter) + '"'
            text["previousStatement"]="null"
            text["nextStatement"]="null"

            arg_counter += 1
            toolbox[GetClassName(gp)].append(text)

            # use the same argument type dict
            argument_type_dict[text['type'].strip('"')] = self_argument_types

            # now for function
            func_str = 'function(block){return Blockly.Lua.valueToCode(block, "thisobj", Blockly.Lua.ORDER_TABLE_ACCESS)+"."+"' + GetName(gp) + '="+Blockly.Lua.valueToCode(block, "arg0", Blockly.Lua.ORDER_NONE)+"\\n"}'
            functions[text['type'].strip('"')] = func_str


        # do something with:item_type item_name params
        # print(item_name)
        # print(params)

def parse_function_params(param_text):
    param_text = param_text.strip()
    ret = []
    if len(param_text) == 0:
        return ret
    for param in param_text.split(','):
        param = re.sub(r'\[([a-zA-Z0-9:]+)\]\([a-zA-Z0-9/\._]+\)',r'\1',param).strip()
        match = re.match(r'^([^ ]+)( +([^ ]+))?( *= *([^ ]+))?$',param)
        assert match, f'not match {param}'
        ret.append({
            'type':match.group(1),
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

            # TODO RoomDescriptor::List type

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
            print(line)

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
                # TODO generate function
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
                argument_type_dict[text['type']] = self_argument_types
            elif current_subtitle == 'Variables':
                continue
            elif current_subtitle == 'Constructors':
                args = parse_function_params(GetArgListText(gp))
                continue
            elif current_subtitle == 'Functions':
                # TODO:fix GetPtrHash
                # TODO:fix Isaac.GridSpawn
                args = parse_function_params(GetArgListText(gp))
                continue
            else:
                assert False, f'unknown subtitle {current_subtitle} in {class_file_name}'
        




# enumerate

def parse_enums(md_text,enum_name):

    assert enum_name != 'ModCallbacks', 'ModCallbacks file format is not same with others'

    found_header = None
    first_elem = True

    item_count = 0

    dup_hash = enum_name

    print("GOT:" + enum_name)
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


for class_md in glob(f'{LUA_DOC_DIR}/docs/*.md'):
    class_name = class_md.split('\\')[-1][:-3]
    if class_name in [
        'PLACEHOLDER',
        'index',
        ]:
        continue
    print(f'parse class file : {class_md}')

    with open(class_md) as f:
        parse_class(f.read(),class_name)

# raise 'stop'

for enum_md in glob(f'{LUA_DOC_DIR}/docs/enums/*.md'):
    enum_name = enum_md.split('\\')[-1][:-3]
    with open(enum_md) as f:
        if enum_name == 'ModCallbacks':
            parse_mod_callback_enum(f.read()) 
        else:
            parse_enums(f.read(),enum_name)
# with open(LUA_DOC_DIR + '/group__enums.html') as f:
#     parse_enums(f.read(),MOD_DOC_WEB_DIR + '/')

# # first scan
# for k in inhert:
#     parent = inhert[k]
#     child = k
#     if not parent in inhert_cluster:
#         inhert_cluster[parent]=[ parent ]
#     inhert_cluster[ parent ].append(child)
# # cluster
# stop_cluster = False
# while not stop_cluster:
#     stop_cluster = True
#     for elem in inhert_cluster:
#         for elem_child in inhert_cluster[elem]:
#             if elem_child in inhert_cluster:
#                 # elem_child_child -> elem
#                 for elem_child_child in inhert_cluster[elem_child]:
#                     if not elem_child_child in inhert_cluster[elem]:
#                         inhert_cluster[elem].append(elem_child_child)
#                         stop_cluster = False
# ↑ It is so beautiful that I bought a vernier caliper


# exit(0)

# with open(LUA_DOC_DIR + '/group__funcs.html') as f:
#     parse_class_text(f.read(),True,MOD_DOC_WEB_DIR + '/group__funcs.html')

# for ns in ['/namespace_isaac.html','/namespace_input.html']:
#     with open(LUA_DOC_DIR + ns) as f:
#         parse_class_text(f.read(),True,MOD_DOC_WEB_DIR + ns)

# for clss in glob(LUA_DOC_DIR + "/class*.html"):
#     if clss.endswith('-members.html'):
#         continue
#     with open(clss.replace('\\','/')) as f:
#         parse_class_text(f.read(),False,MOD_DOC_WEB_DIR + clss.replace('\\','/')[len(LUA_DOC_DIR):])

#patch: replace all integer to math_number
type_output_replace = {
    "integer":"Number",
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
    if block == 'Isaac::GetPlayer':
        return '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'
    if block == 'Game::GetPlayer':
        return '<value name="thisobj"><shadow type="Game"></shadow></value>'+\
        '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'
    if block == 'Level::GetName':
        return '\
        <value name="thisobj">\
          <block type="Game::GetLevel">\
            <value name="thisobj">\
              <block type="Game"></block>\
            </value>\
          </block>\
        </value>\
        <value name="arg0">\
          <shadow type="logic_null"></shadow>\
        </value>\
        <value name="arg1">\
          <shadow type="logic_null"></shadow>\
        </value>\
        <value name="arg2">\
          <shadow type="logic_null"></shadow>\
        </value>\
        <value name="arg3">\
          <shadow type="logic_null"></shadow>\
        </value>\
        <value name="arg4">\
          <shadow type="logic_null"></shadow>\
        </value>'
    
    # the default value
    ret = ''
    if block in argument_type_dict:
        type_dict = argument_type_dict[block]
        for argname in type_dict:
            if type_dict[argname] == 'Game':
                ret += '<value name="{arg}"><block type="Game"></block></value>'.format(arg=argname)
            if type_dict[argname] == 'EntityPlayer':
                ret += ('<value name="{arg}"><shadow type="Isaac::GetPlayer">'+\
                    '<value name="arg0"><shadow type="math_number"><field name="NUM">0</field></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'MusicManager':
                ret += '<value name="{arg}"><block type="MusicManager"></block></value>'.format(arg=argname)
            if type_dict[argname] == 'Font':
                ret += ('<value name="{arg}"><shadow type="Game::GetFont">'+\
                    '<value name="thisobj"><shadow type="Game"></shadow></value>'+\
                    '</shadow></value>').format(arg=argname)
            if type_dict[argname] == 'Level':
                ret += ('<value name="{arg}"><block type="Game::GetLevel">'+\
                    '<value name="thisobj"><block type="Game"></block></value>'+\
                    '</block></value>').format(arg=argname)
            if type_dict[argname] == 'Room':
                ret += ('<value name="{arg}"><block type="Game::GetRoom">'+\
                    '<value name="thisobj"><block type="Game"></block></value>'+\
                    '</block></value>').format(arg=argname)
            if type_dict[argname] == 'Seeds':
                ret += ('<value name="{arg}"><block type="Game::GetSeeds">'+\
                    '<value name="thisobj"><block type="Game"></block></value>'+\
                    '</block></value>').format(arg=argname)
            if type_dict[argname] == 'SFXManager':
                ret += ('<value name="{arg}"><block type="SFXManager"></block></value>').format(arg=argname)
    return ret


# generate json

json_str = None

# toolbox[""] is global function
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

