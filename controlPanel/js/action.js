

$("#song_lang").change(function(){
    var lang = this.value;
    var engOptions = '<option value="havana">havana</option>\
        <option value="something just like this">something just like this</option>\
        <option value="shape of you">shape of you</option>\
        <option value="don \' t let me down">don \' t let me down</option>\
        <option value="how long">how long</option>\
        <option value="thunder">thunder</option>\
        <option value="believer">believer</option>\
        <option value="in the end">in the end</option>\
        <option value="lily">lily</option>\
        <option value="faded">faded</option>\
        <option value="see you again">see you again</option>\
        <option value="let her go">let her go</option>\
        <option value="that girl">that girl</option>\
        <option value="cry on my shoulder">cry on my shoulder</option>\
        <option value="until you">until you</option>\
        <option value="the day you went away">the day you went away</option>\
        <option value="beautiful in white">beautiful in white</option>\
        <option value="despacito">despacito</option>\
        <option value="girls like you">girls like you</option>\
        <option value="i love you 3000">i love you 3000</option>\
        <option value="we don \' t talk anymore">we don \' t talk anymore</option>\
        <option value="whatever it takes">whatever it takes</option>\
        <option value="birds">birds</option>';
    
    var jaOptions = '<option value="歌に形はないけれど">歌に形はないけれど</option>\
        <option value="君がくれたもの">君がくれたもの</option>\
        <option value="恋愛サーキュレーション">恋愛サーキュレーション</option>\
        <option value="テルーの唄">テルーの唄</option>\
        <option value="涙の物語">涙の物語</option>\
        <option value="さくらあなたに出会えてよかった">さくらあなたに出会えてよかった</option>\
        <option value="ひらりひらり">ひらりひらり</option>\
        <option value="蛍">蛍</option>\
        <option value="さよならの夏">さよならの夏</option>\
        <option value="シルエット">シルエット</option>';

    var viOptions = '<option value="anh nhà ở đâu thế">anh nhà ở đâu thế</option>\
        <option value="bạc_phận">bạc_phận</option>\
        <option value="độ ta không độ nàng">độ ta không độ nàng</option>\
        <option value="sóng gió">sóng gió</option>\
        <option value="lãng_quên chiều thu">lãng_quên chiều thu</option>\
        <option value="hai triệu năm">hai triệu năm</option>\
        <option value="để mị nói cho mà nghe">để mị nói cho mà nghe</option>\
        <option value="vẽ">vẽ</option>\
        <option value="người ta nói">người ta nói</option>\
        <option value="gió vẫn hát">gió vẫn hát</option>\
        <option value="có chàng_trai viết lên cây">có chàng_trai viết lên cây</option>\
        <option value="trọn tình">trọn tình</option>\
        <option value="lớn rồi còn khóc_nhè">lớn rồi còn khóc_nhè</option>';

    if (lang == "vi"){
        $("#song").empty().append(viOptions);
    } else if (lang == "en"){
        $("#song").empty().append(engOptions);
    } else if (lang == "ja"){
        $("#song").empty().append(jaOptions);
    }
    $("#song").prop("selectedIndex", 0);
    $("#song-button .ui-selectmenu-button-text").text($("#song :selected").text());
});

var actionServerUrl = serverUrl + "/conversations/controlpanel/execute";
var eventAppendServerUrl = serverUrl + "/conversations/controlpanel/tracker/events";

function executeAction(action_name){
    var data = {
        "name":action_name,
    }
    $.ajax({
        type: "POST",
        url: actionServerUrl,
        data: JSON.stringify(data),
        dataType: 'JSON',
        contentType: 'application/json',
        success: function(response){
            console.log(response);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log(xhr.status);
            console.log(thrownError);
        }
    });
}

function setSlot(slotName , slotValue){
    var data = {
        "event":"slot",
        "name":slotName,
        "value":slotValue
    }
    $.ajax({
        type: "POST",
        url: eventAppendServerUrl,
        data: JSON.stringify(data),
        dataType: 'JSON',
        contentType: 'application/json',
        success: function(response){
            console.log(response);
            if (slotName == "song_name"){
                executeAction("action_nao_sing");
            } else if (slotName == "dance_name"){
                executeAction("action_nao_dance");
            } else if (slotName == "action"){
                executeAction("action_action");
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log(xhr.status);
            console.log(thrownError);
        }
    });
}

function setSlots(slots, action_name){
    var data = [];
    for(var name in slots) {
        var value = slots[name];
        data.push({
            "event":"slot",
            "name":name,
            "value":value
        });
    }

    $.ajax({
        type: "POST",
        url: eventAppendServerUrl,
        data: JSON.stringify(data),
        dataType: 'JSON',
        contentType: 'application/json',
        success: function(response){
            console.log(response);
            executeAction(action_name);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log(xhr.status);
            console.log(thrownError);
        }
    });
}

$('#dance-form').submit(function(event){
    event.preventDefault();
    setSlot("dance_name" , $('#dance').val());
    return false;
});

$('#song-form').submit(function(event){
    event.preventDefault();
    setSlot("song_name" , $('#song').val());
    return false;
});

$(".btn-action").click(function(){
    setSlot("action", $(this).data("action"));
}); 

$(".btn-mode").click(function(){
    var slots = {
        "mode_action" : $(this).data("mode_action"),
        "mode" : $(this).data("mode"),
    }
    setSlots(slots, "action_mode");
});

$("#btn-volume-adjust").click(function(){
    var slots = {
        "mode_action" : $("#volume").val(),
        "mode" : "volume",
    }
    setSlots(slots, "action_mode");
}); 

$("#btn-talk-text").click(function(){
    var slots = {
        "lang" : $("#talkLang").val(),
        "say_text" : $("#talk-text").val(),
    }
    setSlots(slots, "action_nao_say_text");
}); 
