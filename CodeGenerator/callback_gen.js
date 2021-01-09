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
    const m_new = TMSG[`__TXT_${old}`]
    console.error(`${old} => ${m_new}`)
    return m_new
})
if(save_to){
    writeFileSync(save_to,replaced,{encoding:'utf8'})
}else{
    console.log(replaced)
}



