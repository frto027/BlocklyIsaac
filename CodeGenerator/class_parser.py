# MIT License

# Copyright (c) 2020 frto027

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


from bs4 import BeautifulSoup
from bs4 import element
from glob import glob
import re
LUA_DOC_DIR = "CodeGenerator/IsaacDocs"  # """CodeGenerator/LuaDocs"""
MOD_DOC_WEB_DIR = "" # "https://moddingofisaac.com/docs" see function get_blk_help at blockly_inject.js

"""
group:
1 0 static
2 1 const
3 2 返回值（整体）包含(4 7)
4 3 返回值类型
7 6 返回值的&标记

8 7 命名空间/类名
10 9 函数/成员名字
"""
FUNC_NAME_REG = re.compile('^(static )?(const )?((([_a-zA-Z0-9]+::)*([_a-zA-Z0-9]+))(&)? )?(([_a-zA-Z0-9]+::)*)([_a-zA-Z0-9]+)$')

def IsStatic(groups):
    return not groups[0] == None
def IsConst(groups):
    return not groups[1] == None
def GetRetType(groups):
    if IsCtor(groups):
        return GetClassName(groups).strip('::')
    if groups[3] == None:
        return None
    return convert_text_type(groups[3])
def IsRetRef(groups):
    return not groups[6] == None
def GetClassName(groups):
    return groups[7]
def GetName(groups):
    return groups[9]
def IsCtor(groups):
    return GetClassName(groups).strip('::').split('::')[-1] == GetName(groups)

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

callback_func_arg_reg = re.compile('Function Args:.?\\(([a-zA-Z\\[\\] ,]+)\\)')
callback_func_add_arg_reg = re.compile('Optional callback Args: ?([a-zA-Z]+)')

callback_args = {}
callback_add_args = {}
def handleCallbackArguments(callback_name,text):
    arg_result = callback_func_arg_reg.search(text)
    if arg_result:
        callback_args[callback_name] = []
        arg_result = re.split(', ?',arg_result.group(1))
        for arg in arg_result:
            name_gp = re.match('^([a-zA-Z]+) ?\\[([a-zA-Z]+)\\]$',arg)
            if name_gp:
                arg_name = name_gp[1]
                arg_type = name_gp[2]
            else:
                assert re.match('^[a-zA-Z]+$',arg), "can't match ModCallbacks argument text."
                arg_name = callback_name + "_callbackArg"
                arg_type = arg
            arg_type = convert_text_type(arg_type)
            arg_name = '[' + apply_translate(arg_type,callback_name,True) + ']' + apply_translate(arg_name,callback_name)
            callback_args[callback_name].append({"type":arg_type,"name":arg_name})
            # print(arg_name)
            # print(arg_type)

        # arg_result is array of arguments
    add_arg_result = callback_func_add_arg_reg.search(text)
    if add_arg_result:
        add_arg_result = add_arg_result.group(1)
        add_arg_result = convert_text_type(add_arg_result)
        callback_add_args[callback_name]={"type":add_arg_result,"name":"["+apply_translate(add_arg_result,callback_name,True)+"]"}
        # add_arg_result is string of argument type
        # print(add_arg_result)
    pass

toolbox = {}
functions = {}
def parse_class_text(text,is_namespace,file_path):
    soup = BeautifulSoup(text,'html.parser')
    for item in soup.find_all(attrs={"class":'memitem'}):
        href_url = file_path + item.find_previous_sibling(attrs={"class":'memtitle'}).find('a')['href']

        item_table = item.find('table', attrs={"class":'memname'})
        item_name = item_table.find('td', attrs={"class":'memname'}).text.strip()
        item_name = convert_text_name(item_name)

        param_types = item_table.find_all(attrs={"class":'paramtype'})
        param_names = item_table.find_all(attrs={"class":'paramname'})

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
            text['message0'] += " "+apply_translate("target",dup_hash)+"[" + apply_translate(GetClassName(gp).strip('::'),dup_hash,True) +"] %2"
            text['args0'] += ',{"type":"input_value","name":"thisobj","check":"'+GetClassName(gp).strip('::')+'",align:"RIGHT"}'
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
        # a. or a:
        if not is_namespace and not IsStatic(gp):
            if not IsCtor(gp):
                ret_str += "Blockly.Lua.valueToCode(block, 'thisobj', Blockly.Lua.ORDER_ATOMIC)"
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
                func_str += "[" + ret_str + ",Blockly.Lua.ORDER_ATOMIC]"
            else:
                func_str += "[" + ret_str + ",Blockly.Lua.ORDER_HIGH]"

        func_str+="}"
        functions[text['type'].strip('"')] = func_str
        
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

            # now for function
            func_str = 'function(block){return Blockly.Lua.valueToCode(block, "thisobj", Blockly.Lua.ORDER_ATOMIC)+"."+"' + GetName(gp) + '="+Blockly.Lua.valueToCode(block, "arg0", Blockly.Lua.ORDER_NONE)}'
            functions[text['type'].strip('"')] = func_str


        # do something with:item_type item_name params
        # print(item_name)
        # print(params)


# enumerate

def parse_enums(text,folder_path):
    soup = BeautifulSoup(text,'html.parser')
    
    for item in soup.find_all(attrs={"class":'memitem'}):
        enum_name = item.find(attrs={"class":'memname'}).find('a').text.strip()
        first = True
        first_elem = True

        dup_hash = enum_name

        # print("GOT:" + enum_name)
        text = {}
        text["type"] = '"' + enum_name + '"'
        text['message0'] = '"[' + apply_translate(enum_name,dup_hash,True) + '] %1 "'
        text['args0'] = '[{"type": "field_dropdown","name": "ENUM_VAL","options":['
        help_url = ''
        for ch in item.find(attrs={"class":'memdoc'}).find('table').children:
            if isinstance(ch, element.Tag) and ch.name == 'tr':
                if first:
                    first = False
                    help_url = folder_path + ch.find_parent(attrs={"class":'memitem'}).find(attrs={"class":'memproto'}).find('a')['href']
                    continue
                field_name = ch.find(attrs={"class":"fieldname"}).text.strip()
                field_doc = ch.find(attrs={"class":"fielddoc"}).text.strip()

                # some callbacks parse with wrong space, so I patch the script
                # it turns 'MC_PRE_ROOM_ENTITY_SPAWNFunction Args......' into 'MC_PRE_ROOM_ENTITY_SPAWN\xa0Function Args......'
                if enum_name == "ModCallbacks" and re.search('MC_[A-Z_]+Function',field_name):
                    mid = re.search('(MC_[A-Z_]+)Function',field_name).span(1)[1]
                    print('update modcallbacks, before:')
                    print('\t' + field_name)
                    field_name = field_name[:mid] + '\xa0' + field_name[mid:]
                    print('after:')
                    print('\t' + field_name)

                if field_name.find('\xa0') > 0:
                    handleCallbackArguments(field_name[0:field_name.find('\xa0')],field_name[field_name.find('\xa0'):])
                    field_name = field_name[0:field_name.find('\xa0')]
                    assert enum_name == "ModCallbacks"
                
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

                text['args0'] += '["'+ apply_translate(field_name,dup_hash) + field_doc + '","' + field_name +'"]'

                # print("name{"+field_name+"}")
                # print("doc{"+field_doc+"}")
        text['args0'] += ']}'
        text['args0'] += ']'
        text['output'] = '"' + enum_name + '"'
        # text['output'] = '"Number"'
        text['tooltip']='"'+enum_name+'"'
        text['colour']='122'
        text['helpUrl']='()=>get_blk_help("' + help_url + '")'
        if not 'Enums' in toolbox:
            toolbox['Enums'] = []
        toolbox['Enums'].append(text)

        # functions for enum
        func_str = "function (block){ return ['" + enum_name + ".'+ block.getFieldValue('ENUM_VAL'),Blockly.Lua.ORDER_ATOMIC]}"
        functions[text['type'].strip('"')] = func_str

        # all enums are number
        typealias[enum_name]='Number'




with open(LUA_DOC_DIR + '/group__enums.html') as f:
    parse_enums(f.read(),MOD_DOC_WEB_DIR + '/')

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

with open(LUA_DOC_DIR + '/group__funcs.html') as f:
    parse_class_text(f.read(),True,MOD_DOC_WEB_DIR + '/group__funcs.html')

for ns in ['/namespace_isaac.html','/namespace_input.html']:
    with open(LUA_DOC_DIR + ns) as f:
        parse_class_text(f.read(),True,MOD_DOC_WEB_DIR + ns)

for clss in glob(LUA_DOC_DIR + "/class*.html"):
    if clss.endswith('-members.html'):
        continue
    with open(clss.replace('\\','/')) as f:
        parse_class_text(f.read(),False,MOD_DOC_WEB_DIR + clss.replace('\\','/')[len(LUA_DOC_DIR):])

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
    return ''


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

