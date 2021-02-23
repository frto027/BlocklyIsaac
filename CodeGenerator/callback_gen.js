/**
MIT License

Copyright (c) 2021 frto027

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

/**
 * This is a callback svg translate generater
 */
const { readFileSync, writeFileSync } = require("fs")
const assert = require('assert')

let [,prog,svg,translate,save_to] = process.argv


if(svg == undefined || !svg.endsWith('.svg') || translate == undefined || !translate.endsWith('.js')){
    console.log(`
    usage:
        node ${prog} <path of Isaac Callbacks.svg> <path of translate file(TMSG is defined).js> <save_to.svg>
    
    the svg will translate, and output to save_to.svg or stdout

    for example:
        node ${prog} ../media/callbacks/IsaacCallbacks_en.svg ../code_translate/zh-hans.js ../media/callbacks/IsaacCallbacks_zh-hans.svg
    `)
    process.exit(-1)
}

let TMSG = undefined
eval(readFileSync(translate,{encoding:'utf8'}))
assert(TMSG != undefined, `wrong:${translate}`)

const reg = /MC_[A-Z_]+/g

let origin = readFileSync(svg,{encoding:'utf8'})

let replaced = origin.replace(reg,(old)=>{
    const m_new = TMSG[`__TXT_${old}`] || old
    console.error(`${old} => ${m_new}`)
    return m_new
})

let translate_dict = [
    [
        `Checks every Frame if "Mute" or "Fullscreen" action is triggered`,
        `在每一帧，检查“静音”或“全屏”动作是否被触发`
    ],
    [
        `Check if "Mute", "Fullscreen", "Restart" or "Console" action is triggered`,
        `检查“静音”、“全屏”、“重启”或“控制台”动作是否被触发`
    ],
    [
        `Functions without a direct arrow connection are called in the loading order of the current entities in the room`,
        `没有直接连接箭头的函数会按照房间中各个实体的载入顺序来运行`
    ],
    [
        `Execution order`,`运行的顺序`
    ],
    [
        `Usage of a function`,`函数的使用`
    ],
    [
        `only if something specific changed`,
        `当且仅当某些特性被改变时`
    ],
    [
        `Newly initialized Entities will NOT get an Update signal in the same render loop<br />But they will trigger a RENDER signal right away`,
        `新初始化的实体<b>不会</b>在当前的渲染循环中收到“更新”信号<br />但是它们会立即触发一个“渲染”信号`
    ],
    [
        `<b>BUG?</b> <br />Called once when consuming an unidentified pill<br />OR<br />Called every frame while holding an identified pill`,
        `<b>BUG?</b> <br />当使用未辨认的药丸时会执行一次<br />或者<br />当持有已辨认的药丸时，每帧执行`
    ],
    [
        `everything is ready`,
        `一切就绪`
    ],
    [
        `Spawn Effects`,
        `生成各种效果`
    ],
    [
        `post effect update if needed`,
        `如有必要，触发效果更新`
    ],
    [
        `Update every cache flag`,
        `更新每个缓存标记`
    ],
    [
        `Game Start`,
        `游戏开始`
    ],
    [
        `Game closed`, `关闭游戏`
    ],
    [
        `Called when you die or win the game`,
        `当你死亡或赢得游戏时调用`
    ],
    [
        `Game logic can keep going till you exit the death screen`,
        `在你退出死亡界面之前，游戏逻辑会继续执行`
    ],
    [
        `Check all main input actions`,
        `检查所有的主要输入动作`
    ],
    [
        `Entered new Level`,
        `进入新关卡`
    ],
    [
        `Game Logic loop`,
        `“游戏”逻辑循环`
    ],
    [
        `UPDATE logic loop`,
        `“更新”逻辑循环`
    ],
    [
        `UPDATE Logic`,
        `“更新”逻辑`
    ],
    [
        `TEAR SPAWN Logic`,
        `“眼泪生成”逻辑`
    ],
    [
        `SPAWN Logic`,
        `“生成”逻辑`
    ],
    [
        `every Frame`,
        `每帧`
    ],
    [
        `UNUSED FUNCTION`,
        `未使用的函数`
    ],
    [
        `Called when a specific function is used`,
        `当使用特定的函数时，会被调用`
    ],
    [
        `Viewer does not support full SVG 1.1`,
        `此视图不能完全支持SVG 1.1(页面显示不完整，请使用新版本的浏览器访问此页)`
    ],
    [
        `is called 49 times per game logic step, so around ~1470/sec`,
        `在每次游戏逻辑步中被调用49次，所以大约每秒1470次`
    ],
    [
        `All  render callbacks are<br />called every 0.5 game logic steps <br />(30 logic steps per second)`,
        `所有渲染回调每0.5个游戏逻辑步调用一次（每秒30个逻辑步）`
    ],
    [
        `All  update callbacks are<br />called every game logic step <br />(30 logic steps per second)`,
        `所有更新回调每个逻辑步调用一次（每秒30个逻辑步）`
    ]
]

for(rep in translate_dict){
    let old
    do{
        old = replaced
        replaced = replaced.replace(translate_dict[rep][0],translate_dict[rep][1])
    }while(old != replaced)
}

if(save_to){
    writeFileSync(save_to,replaced,{encoding:'utf8'})
}else{
    console.log(replaced)
}



