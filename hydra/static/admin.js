"use strict";

var getGroupElements = function(groupId) {
    return document.getElementById(groupId).getElementsByTagName("input");
}

var getMaster = function(groupId){
    return getGroupElements(groupId)[0];
}

var setGroupCheckedState = function(groupId, state) {
    for(let elem of getGroupElements(groupId)) { 
        elem.checked = state;
    }
};

var toggleGroup = function(element, groupId) {
    setGroupCheckedState(groupId, element.checked);
};

var toggleMaster = function(element, groupId) {
    if(!element.checked) {
        getMaster(groupId).checked = false;
    }
}


