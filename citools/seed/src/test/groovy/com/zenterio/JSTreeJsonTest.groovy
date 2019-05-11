package com.zenterio

import java.beans.PropertyDescriptor


class JSTreeJsonTest extends GroovyTestCase {

    JSTreeJson renderer

    @Override
    protected void setUp() {
        this.renderer = new JSTreeJson<Data>(Data.class)
    }

    protected Object getTestData() {
        Data data = new Data()
        data.with {
            arr = [new Object()] as Object[]
            map = ["A": 1]
            ref = new Data()
            strField = "A"
            booleanField = true
        }
        data.ref.with {
            arr = [new Object()] as Object[]
            map = ["B": 2]
            ref = new Data()
            strField = "B"
            booleanField = false
        }
        data.ref.ref.with {
            arr = [new Object()] as Object[]
            map = ["C": 3]
            ref = new Data()
            strField = "C"
            booleanField = true
        }
        return data
    }

    public void testGetId() {
        assert this.renderer.getId(null) == "null@0"
        assert this.renderer.getId(null) == "null@1"
        assert this.renderer.getId(null) == "null@2"
    }

    public void testGetParentIdRoot() {
        assert this.renderer.getParentId(new ArrayList<Data>()) == "#"
    }

    public void testGetParentId() {
        Data d = new Data()
        assert this.renderer.getParentId([d] as ArrayList<Data>) == this.renderer.getId(d)
        assert this.renderer.getParentId([new Data(), d] as ArrayList<Data>) == this.renderer.getId(d)
    }

    public void testJsonTreeNodeNullValueWithNodeName() {
        this.renderer.jsonTreeNode("Name", null)
        String json = this.renderer.getContent()
        String expected = """\
{"id":"null@0","parent":"#","text":"<span class='zenterio-header'>Name</span>","state":{"opened":"true"}}"""
        assert json == expected
    }

    public void testJsonTreeNodeNullNodeNameWithValue() {
        String value = "Value"
        String id = this.renderer.getId(value)
        this.renderer.jsonTreeNode(null, value)
        String json = this.renderer.getContent()
        String expected = """\
{"id":"${id}","parent":"#","text":"<span class='zenterio-header'>Value</span>","state":{"opened":"true"}}"""
        assert json == expected
    }

    public void testJsonTreeNodeNullNodeNameNullValue() {
        this.renderer.jsonTreeNode(null, null)
        String json = this.renderer.getContent()
        String expected = """\
{"id":"null@0","parent":"#","text":"<span class='zenterio-header'>NULL</span>","state":{"opened":"true"}}"""
        assert json == expected
    }

    public void testJsonTreeNodeSingleLineString() {
        String value = "Value"
        String id = this.renderer.getId(value)
        this.renderer.jsonTreeNode("Name", value)
        String json = this.renderer.getContent()
        String expected = """\
{"id":"${id}","parent":"#","text":"<span class='zenterio-header'>Name: Value</span>","state":{"opened":"true"}}"""
        assert json == expected
    }

    public void testJsonTreeNodeMultiLineString() {
        String value = 'Line 1\nLine 2'
        String id = this.renderer.getId(value)
        String nodeName = "Name"
        this.renderer.jsonTreeNode(nodeName, value)
        String json = this.renderer.getContent()
        String expected = """\
{"id":"null@0","parent":"#","text":"<span class='zenterio-header'>Name</span>","state":{"opened":"true"}},
{"id":"${id}","parent":"null@0","text":"<div class='zenterio-content'>Line 1\\nLine 2</div>","state":{"opened":"true"}}\
"""
        assert json == expected
    }

    public void testGetObjectHeader() {
        Object o = new Object()
        String id = this.renderer.getId(o)
        String expected = "java.lang.Object@${id}"
        assert this.renderer.getObjectHeader(o) == expected
    }

    public void testGetObjectHeaderForNull() {
        assert this.renderer.getObjectHeader(null) == "NULL"
    }

    public void testGetObjectHeaderForMap() {
        Map map = [:]
        String id = this.renderer.getId(map)
        String expected = "java.util.LinkedHashMap@${id}"
        assert this.renderer.getObjectHeader(map) == expected
    }

    public void testNullToJson() {
        String expected = """\
[{"id":"null@0","parent":"#","text":"<span class='zenterio-header'>NULL</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(null) == expected
    }

    public void testStringToJson() {
        String s = "s"
        String id = this.renderer.getId(s)
        String expected = """\
[{"id":"${id}","parent":"#","text":"<span class='zenterio-header'>s</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(s) == expected
    }

    public void testIntegerToJson() {
        String id = this.renderer.getId(1)
        String expected = """\
[{"id":"${id}","parent":"#","text":"<span class='zenterio-header'>1</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(1) == expected
    }

    public void testListToJson() {
        String a = "A"
        String b = "B"
        String idA = this.renderer.getId(a)
        String idB = this.renderer.getId(b)
        List<String> list = [a, b]
        String idL = this.renderer.getId(list)
        String expected = """\
[{"id":"${idL}","parent":"#","text":"<span class='zenterio-header'>java.util.ArrayList@${idL}</span>","state":{"opened":"true"}},
{"id":"${idA}","parent":"${idL}","text":"<span class='zenterio-header'>[0]: A</span>","state":{"opened":"true"}},
{"id":"${idB}","parent":"${idL}","text":"<span class='zenterio-header'>[1]: B</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(list) == expected
    }

    public void testArrayToJson() {
        Integer[] arr = [100, 200]
        String idArr = this.renderer.getId(arr)
        String id0 = this.renderer.getId(arr[0])
        String id1 = this.renderer.getId(arr[1])
        String expected = """\
[{"id":"${idArr}","parent":"#","text":"<span class='zenterio-header'>[Ljava.lang.Integer;@${idArr}</span>","state":{"opened":"true"}},
{"id":"${id0}","parent":"${idArr}","text":"<span class='zenterio-header'>[0]: 100</span>","state":{"opened":"true"}},
{"id":"${id1}","parent":"${idArr}","text":"<span class='zenterio-header'>[1]: 200</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(arr) == expected
    }

    public void testMapToJson() {
        Map map = ["key": "Value"]
        String idM = this.renderer.getId(map)
        String idValue = this.renderer.getId(map['key'])
        String expected = """\
[{"id":"${idM}","parent":"#","text":"<span class='zenterio-header'>java.util.LinkedHashMap@${idM}</span>","state":{"opened":"true"}},
{"id":"${idValue}","parent":"${idM}","text":"<span class='zenterio-header'>[key]: Value</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(map) == expected
    }

    public void testObjectToJson() {
        Object o = new Object()
        String id = this.renderer.getId(o)
        String expected = """\
[{"id":"${id}","parent":"#","text":"<span class='zenterio-header'>java.lang.Object@${id}</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(o) == expected
    }

    public void testComplexObject() {
        Data d = new Data()
        String idD = this.renderer.getId(d)
        String idA = this.renderer.getId(d.arr)
        String idB = this.renderer.getId(d.booleanField)
        String idL = this.renderer.getId(d.list)
        String idM = this.renderer.getId(d.map)
        String idS = this.renderer.getId(d.strField)

        String result = this.renderer.toJson(d)
        String expected = """\
[{"id":"${idD}","parent":"#","text":"<span class='zenterio-header'>com.zenterio.Data@${idD}</span>","state":{"opened":"true"}},
{"id":"${idA}","parent":"${idD}","text":"<span class='zenterio-header'>arr: [Ljava.lang.Object;@${idA}</span>","state":{"opened":"true"}},
{"id":"${idB}","parent":"${idD}","text":"<span class='zenterio-header'>booleanField: true</span>","state":{"opened":"true"}},
{"id":"${idL}","parent":"${idD}","text":"<span class='zenterio-header'>list: java.util.ArrayList@${idL}</span>","state":{"opened":"true"}},
{"id":"${idM}","parent":"${idD}","text":"<span class='zenterio-header'>map: java.util.LinkedHashMap@${idM}</span>","state":{"opened":"true"}},
{"id":"null@0","parent":"${idD}","text":"<span class='zenterio-header'>ref</span>","state":{"opened":"true"}},
{"id":"${idS}","parent":"${idD}","text":"<span class='zenterio-header'>strField: </span>","state":{"opened":"true"}}]"""
        assert result == expected
    }

    public void testToJsonTurnOffIdPrinting() {
        this.renderer.printId = false
        Object o = new Object()
        String expected = "java.lang.Object"
        assert this.renderer.getObjectHeader(o) == expected
    }

    public void testToJsonTurnOffClassPrinting() {
        this.renderer.printClass = false
        Object o = new Object()
        String id = this.renderer.getId(o)
        String expected = "@${id}"
        assert this.renderer.getObjectHeader(o) == expected
    }

    public void testToJsonValuesAreHtmlAndJsonEscaped() {
        String s = '"quoted"<br/>'
        String id = this.renderer.getId(s)
        String expected = """\
[{"id":"${id}","parent":"#","text":"<span class='zenterio-header'>&quot;quoted&quot;&lt;br&#47;&gt;</span>","state":{"opened":"true"}}]"""
        assert this.renderer.toJson(s) == expected
    }

}

public class Data  {
    Object[] arr
    Map map
    Boolean booleanField
    String strField
    Data ref
    List<String> list

    Data() {
        this.arr = new Object[0]
        this.booleanField = true
        this.strField = ""
        this.map = [:]
        this.list = new ArrayList<String>()
    }

}
