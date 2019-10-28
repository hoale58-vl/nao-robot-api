var chatbotServerUrl = serverUrl + "/webhooks/multilang/chat";
var langChangeUrl = serverUrl + "/webhooks/multilang/lang/change";
var listLang = {
	"en": "en-US",
	"vi": "vi-VN",
	"ja" : "ja-JP"
}
var delayInMilliseconds = 7000;
var noteTextarea = $('#textarea-chatbot');
var instructions = $('#recording-instructions');
var notesList = $('ul#notes');
var noteContent = '';
var text = '';
var SpeechRecognition;
var recognition;
var speechEnd = false;
var stopRecog = false;


function startRecognition(lang){
    try {
        stopRecog = false;
        SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = listLang[lang];
        recognition.onstart = function() {
            $('#btn-listing').attr('tabindex', 1);
            $('#btn-listing').css('background', '#dc3545');
        }
        recognition.onspeechend = function() {
            speechEnd = true;
            $('#chat-with-robot').submit();
        }
        recognition.onerror = function(event) {
            if(event.error == 'no-speech') {
                instructions.text('No speech was detected. Try again.');
            };
        }
        recognition.onend = function(event) {
            $('#btn-listing').attr('tabindex', 0);
            $('#btn-listing').css('background', '#007bff');
            if (!speechEnd && !stopRecog){
                recognition.start();
            }
        }
        // Get all notes from previous sessions and display them.
        /*-----------------------------
            Voice Recognition
        ------------------------------*/
        // If false, the recording will stop after a few seconds of silence.
        // When true, the silence period is longer (about 15 seconds),
        // allowing us to keep recording even when the user pauses.
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 5;
        // This block is called every time the Speech APi captures a line.
        recognition.onresult = function(event) {
            console.log(event);
            // event is a SpeechRecognitionEvent object.
            // It holds all the lines we have captured so far.
            // We only need the current one.
            var current = event.resultIndex;
            // Get a transcript of what was said.
            var transcript = event.results[current][0].transcript;
            // Add the current transcript to the contents of our Note.
            // There is a weird bug on mobile, where everything is repeated twice.
            // There is no official solution so far so we have to handle an edge case.
            var mobileRepeatBug = (current == 1 && transcript == event.results[0][0].transcript);
            if(!mobileRepeatBug) {
                noteContent += transcript;
                noteTextarea.val(noteContent);
                text = noteContent;
                noteContent = '';
            }
        };
        recognition.start();
    }
    catch(e) {
        console.log(e);
    }
}

function scrollTop() {
    $('.demo-chatbox').scrollTop(999999);
    $('.msg-box').scrollTop(999999);
}

function userChat(input)
{
    var msg = `<p id="user-send">`+input+`</p>`;
    $('.msg-box').append(msg);
    scrollTop();
}

function askBot(ask)
{
    var img = $('#bot-send img').eq(0).attr('src');
    var msg = `<p id="bot-send"><img src="`+img+`"> `+ask+`</p>`;
    $('.msg-box').append(msg);
    scrollTop();
}

function ajaxRequestText(text)
{
    var data = {
        "sender": "controlpanel_chatbox",
        "message": text
    }
    $.ajax({
            type: "POST",
            url: chatbotServerUrl,
            data: JSON.stringify(data),
            dataType: 'JSON',
            contentType: 'application/json',
            success: function(response){
                askBot(response["result"]);
                scrollTop();
                setTimeout(function() {
                    if (!speechEnd && !stopRecog){
                        recognition.start();
                    }
                    speechEnd = false;
                }, delayInMilliseconds);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
            }
    });
}

function sendMessageBot()
{
    var input = $('#textarea-chatbot').val();
    var counter = 0;
    var interval_obj = setInterval(function(){
        counter += 1;
        if (input != ''){
            $('#textarea-chatbot').val('');
            userChat(input);
            ajaxRequestText(input);
            clearInterval(interval_obj);
            if (!speechEnd && !stopRecog){
                recognition.start();
            }
            speechEnd = false;
        } else if (counter > 5) {
            clearInterval(interval_obj);
            if (!speechEnd && !stopRecog){
                recognition.start();
            }
            speechEnd = false;
        } else {
            input = $('#textarea-chatbot').val();
        }
    }, 1000);
}

$("#chatBoxLang").change(function(){
    var data = {
        "lang" : this.value
    }
    startRecognition(this.value);
    $.ajax({
        type: "POST",
        url: langChangeUrl,
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
});

scrollTop();
$('#chat-with-robot').submit(function(event){
    event.preventDefault();
    sendMessageBot();
    return false;
});

$('textarea').bind("enterKey",function(e){
    sendMessageBot();
});
$('textarea').keyup(function(e){
    if(e.keyCode == 13)
    {
        $(this).trigger("enterKey");
    }
});

$("#btn-speechrecog").click(function(){
    console.log(stopRecog);
    if (stopRecog){
        $(this).css('background', '#007bff');
        stopRecog = false;
        console.log(stopRecog);
        if (!speechEnd && !stopRecog){
            recognition.start();
        }
    } else {
        $(this).css('background', '#dc3545');
        stopRecog = true;
        console.log(stopRecog);
    }
}); 

