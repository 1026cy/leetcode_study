
// import data from 'proto.json';
const protobufjs = require("protobufjs");
data = {"nested":{"PolicyInfoParam":{"fields":{"id":{"type":"string","id":1}}},"PolicyInfoByTypeIdParam":{"fields":{"policyType":{"type":"string","id":1},"centralId":{"type":"string","id":2},"province":{"type":"string","id":3},"city":{"type":"string","id":4},"downtown":{"type":"string","id":5},"garden":{"type":"string","id":6},"sort":{"type":"uint32","id":7},"pageNum":{"type":"uint32","id":8},"pageSize":{"type":"uint32","id":9}}},"PolicyInfoByTagsIdParam":{"fields":{"id":{"type":"uint32","id":1},"customerTagId":{"type":"uint32","id":2},"keyword":{"type":"string","id":3},"pageNum":{"type":"uint32","id":4},"pageSize":{"type":"uint32","id":5}}},"PolicyInfoByDeptIdParam":{"fields":{"department":{"type":"uint32","id":1},"customized":{"type":"string","id":2},"garden":{"type":"string","id":3},"pageNum":{"type":"uint32","id":4},"pageSize":{"type":"uint32","id":5}}},"PolicyInfoSearchParam":{"fields":{"word":{"type":"string","id":1},"department":{"type":"string","id":2},"policyType":{"type":"string","id":3},"industry":{"type":"string","id":4},"customerIndt":{"type":"string","id":5},"startTime":{"type":"string","id":6},"endTime":{"type":"string","id":7},"province":{"type":"string","id":8},"city":{"type":"string","id":9},"downtown":{"type":"string","id":10},"garden":{"type":"string","id":11},"wholews":{"type":"uint32","id":12},"type":{"type":"uint32","id":13},"sorttype":{"type":"uint32","id":14},"pageNum":{"type":"uint32","id":15},"pageSize":{"type":"uint32","id":16}}}}}
const root = protobufjs.Root.fromJSON(data);

const messageRequest = root.lookupType("PolicyInfoByTypeIdParam");

console.log('------------------------')

// <Buffer 0a 01 33 12 00 1a 00 22 00 2a 00 32 00 38 00 40 01 48 0a>
// <Buffer 0a 01 34 12 00 1a 00 22 00 2a 00 32 00 38 00 40 01 48 0a>
function paramsEncode(a,b) {
    const data2 = {
    centralId: "",
    city: "",
    downtown: "",
    garden: "",
    pageNum: a,
    pageSize: 100,
    policyType: b, // "2":政策通知 “4”：政策文件 “6”：政策公告 3：政策要闻 5：政策解读
    province: "",
    sort: 0,
    }

    const aa = messageRequest.encode(data2).finish().slice()
    return aa
}
console.log(paramsEncode())